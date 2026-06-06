"""
Run once to embed your schema definitions into PGVector.
Usage: python -m scripts.ingest_schema
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector
from src.config import PG_VECTOR_URL, OLLAMA_BASE_URL, OLLAMA_EMBED_MODEL, VECTOR_COLLECTION

# ── Schema documents ─────────────────────────────────────────────────────────
DOCS = [
    Document(
        page_content="""TABLE: customers
Purpose: Stores core identity for every bank client.

Columns:
  customer_id  SERIAL PRIMARY KEY
  full_name    VARCHAR(100)   — customer's full legal name
  email        VARCHAR(100)   — unique contact email
  phone        VARCHAR(20)
  address      TEXT
  created_at   TIMESTAMP

Relations:
  One customer → many accounts  (accounts.customer_id FK)

Typical queries: count customers, find by name/email,
registration trends, newest customers.""",
        metadata={"type": "table", "name": "customers"},
    ),
    Document(
        page_content="""TABLE: accounts
Purpose: Bank accounts owned by customers — savings, checking, or loan.

Columns:
  account_id     SERIAL PRIMARY KEY
  customer_id    INTEGER FK → customers.customer_id
  account_number VARCHAR(20) UNIQUE
  account_type   VARCHAR(20): 'savings' | 'checking' | 'loan'
  balance        NUMERIC(15,2)   — current balance in BDT
  status         VARCHAR(20): 'active' | 'frozen' | 'closed'
  opened_at      TIMESTAMP

Relations:
  N accounts → 1 customer (customer_id)
  1 account  → N transactions (transactions.account_id)

Typical queries: total balance, balance by account type,
highest-balance accounts, active vs frozen counts.""",
        metadata={"type": "table", "name": "accounts"},
    ),
    Document(
        page_content="""TABLE: transactions
Purpose: Full ledger of credits, debits, and transfers per account.

Columns:
  transaction_id   SERIAL PRIMARY KEY
  account_id       INTEGER FK → accounts.account_id
  transaction_type VARCHAR(20): 'credit' | 'debit' | 'transfer'
  amount           NUMERIC(15,2)
  description      TEXT   — human-readable narration
  transaction_date TIMESTAMP
  balance_after    NUMERIC(15,2)   — running balance snapshot

Relations:
  N transactions → 1 account (account_id)

Typical queries: recent transactions, credit/debit totals,
transaction history for an account, largest transactions,
monthly volume, daily summaries.""",
        metadata={"type": "table", "name": "transactions"},
    ),
    Document(
        page_content="""JOIN PATTERN: customers ↔ accounts
Use when a query combines customer identity with account data.

SQL template:
  SELECT c.full_name, c.email,
         a.account_number, a.account_type, a.balance
  FROM customers c
  JOIN accounts a ON a.customer_id = c.customer_id

Use cases: list all accounts per customer, total balance per customer,
filter customers who have a savings account, find customers with frozen accounts.

Aggregate example — total balance per customer:
  SELECT c.full_name, COUNT(a.account_id) AS num_accounts,
         SUM(a.balance) AS total_balance
  FROM customers c
  JOIN accounts a ON a.customer_id = c.customer_id
  GROUP BY c.customer_id, c.full_name
  ORDER BY total_balance DESC;""",
        metadata={"type": "join", "name": "customers_accounts"},
    ),
    Document(
        page_content="""JOIN PATTERN: accounts ↔ transactions
Use when a query combines account data with transaction history.

SQL template:
  SELECT a.account_number, a.account_type,
         t.transaction_type, t.amount, t.transaction_date, t.description
  FROM accounts a
  JOIN transactions t ON t.account_id = a.account_id

Use cases: transaction history of an account, credit/debit breakdown,
accounts with most transactions, average transaction size.

Aggregate example — monthly summary per account:
  SELECT a.account_number,
         DATE_TRUNC('month', t.transaction_date) AS month,
         SUM(CASE WHEN t.transaction_type='credit' THEN t.amount ELSE 0 END) AS credits,
         SUM(CASE WHEN t.transaction_type='debit'  THEN t.amount ELSE 0 END) AS debits
  FROM accounts a
  JOIN transactions t ON t.account_id = a.account_id
  GROUP BY a.account_number, month
  ORDER BY month DESC;""",
        metadata={"type": "join", "name": "accounts_transactions"},
    ),
    Document(
        page_content="""JOIN PATTERN: customers → accounts → transactions (3-table)
Use for end-to-end queries from customer identity through to transaction history.

SQL template:
  SELECT c.full_name, a.account_number, a.account_type,
         t.transaction_type, t.amount, t.transaction_date
  FROM customers c
  JOIN accounts a ON a.customer_id = c.customer_id
  JOIN transactions t ON t.account_id = a.account_id

Use cases: complete transaction history for a named customer,
top customers by total transaction volume, customer financial activity report.

Example — top 5 customers by transaction volume:
  SELECT c.full_name,
         COUNT(t.transaction_id) AS tx_count,
         SUM(t.amount)           AS total_volume
  FROM customers c
  JOIN accounts a ON a.customer_id = c.customer_id
  JOIN transactions t ON t.account_id = a.account_id
  GROUP BY c.customer_id, c.full_name
  ORDER BY total_volume DESC
  LIMIT 5;""",
        metadata={"type": "join", "name": "full_3table"},
    ),
    Document(
        page_content="""REPORT: account balance summary
Shows financial health and distribution across account types.

Key metrics: total accounts, total balance, average balance,
balance breakdown by type (savings/checking/loan), active vs inactive counts.

SQL:
  SELECT account_type,
         COUNT(*)        AS account_count,
         SUM(balance)    AS total_balance,
         AVG(balance)    AS avg_balance,
         MAX(balance)    AS max_balance,
         MIN(balance)    AS min_balance
  FROM accounts
  WHERE status = 'active'
  GROUP BY account_type
  ORDER BY total_balance DESC;""",
        metadata={"type": "report", "name": "account_balance_summary"},
    ),
    Document(
        page_content="""REPORT: daily and monthly transaction analytics
Monitors transaction activity, volume, and trends over time.

Key metrics: transaction count per day/month, credit vs debit volumes,
average transaction size, peak activity dates.

Daily summary SQL:
  SELECT DATE(transaction_date)  AS date,
         COUNT(*)                AS total_tx,
         SUM(CASE WHEN transaction_type='credit' THEN amount ELSE 0 END) AS total_credits,
         SUM(CASE WHEN transaction_type='debit'  THEN amount ELSE 0 END) AS total_debits
  FROM transactions
  GROUP BY DATE(transaction_date)
  ORDER BY date DESC
  LIMIT 30;""",
        metadata={"type": "report", "name": "transaction_analytics"},
    ),
]

def main():
    print(f"Connecting to Ollama at {OLLAMA_BASE_URL} for embeddings...")
    embeddings = OllamaEmbeddings(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_EMBED_MODEL,
    )

    print(f"Initialising PGVector collection '{VECTOR_COLLECTION}'...")
    store = PGVector(
        embeddings=embeddings,
        collection_name=VECTOR_COLLECTION,
        connection=PG_VECTOR_URL,
        use_jsonb=True,
    )

    # Clear existing docs so re-runs are safe
    store.delete_collection()
    store = PGVector(
        embeddings=embeddings,
        collection_name=VECTOR_COLLECTION,
        connection=PG_VECTOR_URL,
        use_jsonb=True,
    )

    print(f"Embedding and storing {len(DOCS)} documents...")
    store.add_documents(DOCS)
    print("Schema ingestion complete.")

if __name__ == "__main__":
    main()

