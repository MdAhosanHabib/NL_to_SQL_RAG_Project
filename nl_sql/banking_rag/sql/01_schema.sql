-- pgvector extension (idempotent)
CREATE EXTENSION IF NOT EXISTS vector;

-- 3 banking tables with FK relations
CREATE TABLE IF NOT EXISTS customers (
    customer_id  SERIAL PRIMARY KEY,
    full_name    VARCHAR(100) NOT NULL,
    email        VARCHAR(100) UNIQUE,
    phone        VARCHAR(20),
    address      TEXT,
    created_at   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id     SERIAL PRIMARY KEY,
    customer_id    INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_type   VARCHAR(20) CHECK (account_type IN ('savings','checking','loan')),
    balance        NUMERIC(15,2) DEFAULT 0.00,
    status         VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active','frozen','closed')),
    opened_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id   SERIAL PRIMARY KEY,
    account_id       INTEGER NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) CHECK (transaction_type IN ('credit','debit','transfer')),
    amount           NUMERIC(15,2) NOT NULL,
    description      TEXT,
    transaction_date TIMESTAMP DEFAULT NOW(),
    balance_after    NUMERIC(15,2)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_accounts_customer ON accounts(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);

