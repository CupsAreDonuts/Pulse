import hashlib
import os
import urllib.parse
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def process():
    load_dotenv()
    latest_csv = get_latest_csv()
    banking_information = pd.read_csv(
        latest_csv, sep=";", encoding="latin1", decimal=","
    )
    pulse_sparkasse = generate_transactions(banking_information)
    engine = generate_engine()

    upsert_sparkasse_transactions(engine=engine, pulse_sparkasse=pulse_sparkasse)
    print(f"Import complete. Processed {len(pulse_sparkasse)} rows.")


def get_latest_csv():
    csv_directory = load_csv_dir()
    csv_files = [csv_file for csv_file in csv_directory.glob("*.CSV")]
    latest_file = max(csv_files, key=os.path.getmtime)
    return latest_file


def load_csv_dir():
    return Path(os.getenv("SPARKASSE_CSV_DIR"))


def generate_transactions(banking_information: pd.DataFrame) -> pd.DataFrame:
    pulse_sparkasse = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                banking_information["Buchungstag"], format='%d.%m.%y', dayfirst=True
            ),
            "source_entity": banking_information["Beguenstigter/Zahlungspflichtiger"],
            "source_account": banking_information["Kontonummer"],
            "amount": banking_information["Betrag"].astype(float),
            "description": banking_information["Verwendungszweck"],
            "category": "Uncategorized",
        }
    )
    pulse_sparkasse = pulse_sparkasse.dropna(subset=['timestamp'])
    pulse_sparkasse["hash_id"] = pulse_sparkasse.apply(
        generate_transaction_id, axis=1
    )
    return pulse_sparkasse


def generate_transaction_id(row):
    transaction_string = (
        f"{row['timestamp']}{row['amount']}{row['description']}{row['source_account']}"
    )
    return hashlib.sha256(transaction_string.encode()).hexdigest()


def generate_engine() -> Engine:
    db_url = get_database_url()
    engine = create_engine(db_url)
    return engine


def get_database_url():
    user = os.getenv("DB_USER")
    pw = urllib.parse.quote_plus(os.getenv("DB_PASSWORD"))
    db_name = os.getenv("DB_NAME")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    return f"postgresql://{user}:{pw}@{host}:{port}/{db_name}"


def upsert_sparkasse_transactions(engine: Engine, pulse_sparkasse: pd.DataFrame):
    # 1. Upload to a temporary staging table
    # 'replace' ensures the temp table is fresh every time the script runs
    pulse_sparkasse.to_sql(
        name='temp_transactions',
        con=engine,
        if_exists='replace',
        index=False,
        method='multi'
    )

    # 2. Execute the Upsert (ON CONFLICT)
    # This moves data from temp -> main only if the hash_id is new
    upsert_query = text("""
        INSERT INTO transactions (timestamp, source_entity, source_account, amount, description, category, hash_id)
        SELECT timestamp, source_entity, source_account, amount, description, category, hash_id
        FROM temp_transactions
        ON CONFLICT (hash_id) DO NOTHING;
    """)

    with engine.begin() as conn:
        conn.execute(upsert_query)
        # 3. Cleanup
        conn.execute(text("DROP TABLE temp_transactions;"))


if __name__ == "__main__":
    process()
