CREATE TABLE IF NOT EXISTS finance_log (
    id SERIAL PRIMARY KEY,
    -- Core
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(12, 2) NOT NULL,
    currency TEXT DEFAUlt 'EUR',
    -- Context
    description TEXT,
    vendor TEXT,
    category TEXT,
    -- Meta
    source_account TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    hash_id TEXT UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_finance_time ON finance_log(timestamp);
