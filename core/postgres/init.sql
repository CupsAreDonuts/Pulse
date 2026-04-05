CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    -- Core
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(12, 2) NOT NULL,
    currency TEXT DEFAUlt 'EUR',
    -- Context
    description TEXT,
    source_entity TEXT,
    source_account TEXT,
    category TEXT,
    -- Meta
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    hash_id TEXT UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_finance_time ON transactions(timestamp);
