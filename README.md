# 🏦 Financial NL-to-SQL RAG

> Ask questions about your banking database in plain English — powered by **LangGraph**, **Ollama (Gemma4)**, and **PGVector** running entirely on local infrastructure.

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-1C3C3C?logo=langchain&logoColor=white)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-FF6B35)](https://langchain-ai.github.io/langgraph/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791?logo=postgresql&logoColor=white)](https://postgresql.org)
[![pgvector](https://img.shields.io/badge/pgvector-0.8+-orange)](https://github.com/pgvector/pgvector)
[![Ollama](https://img.shields.io/badge/Ollama-Gemma4%3A26b-black?logo=ollama)](https://ollama.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---
<img width="1022" height="746" alt="NL_to_SQL" src="https://github.com/user-attachments/assets/3a335b9f-94ed-48a8-9c4e-578fca539090" />


## 📸 Demo

```
╭──────────────────────────────────────────────╮
│ Banking NL-to-SQL RAG                        │
│ LangGraph · Ollama · PostgreSQL              │
│ Type debug to toggle SQL view · quit to exit │
╰──────────────────────────────────────────────╯

You › How many customers do we have?
 total_customers
 10
╭─────────────────── Answer ──────────────────╮
│ There are a total of 10 customers.          │
╰─────────────────────────────────────────────╯

You › Which customer has the highest total balance?
╭─────────────────── Answer ──────────────────╮
│ Priya Das has the highest total balance     │
│ at ৳670,000 across her savings and          │
│ checking accounts.                          │
╰─────────────────────────────────────────────╯
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│  Windows Machine (192.168.0.102)                    │
│  ┌─────────────────────────────────────────────┐   │
│  │  Ollama                      :11434          │   │
│  │   ├── gemma4:26b    (SQL generation)         │   │
│  │   └── nomic-embed-text (schema embedding)   │   │
│  └─────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP API
┌──────────────────────▼──────────────────────────────┐
│  Linux Machine (192.168.0.105)                      │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │  Python 3.13 — LangGraph Agent                │ │
│  │                                               │ │
│  │  Terminal CLI                                 │ │
│  │      │                                        │ │
│  │      ▼                                        │ │
│  │  retrieve_schema ──► PGVector (schema docs)   │ │
│  │      │                                        │ │
│  │      ▼                                        │ │
│  │  generate_sql    ──► Ollama (gemma4:26b)      │ │
│  │      │                                        │ │
│  │      ▼                                        │ │
│  │  execute_sql     ──► PostgreSQL               │ │
│  │      │           ◄── retry loop (≤3x)         │ │
│  │      ▼                                        │ │
│  │  format_answer   ──► Ollama (gemma4:26b)      │ │
│  │      │                                        │ │
│  │      ▼                                        │ │
│  │  Terminal output                              │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  Docker: pgvector/pgvector:pg18  :5432      │   │
│  │   ├── banking_db (3 tables + FK relations)  │   │
│  │   └── langchain_pg_embedding (vector store) │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### LangGraph Pipeline

```
START
  │
  ▼
retrieve_schema   → embed NL question → similarity search PGVector → top-5 schema docs
  │
  ▼
generate_sql      → build prompt with schema context → call gemma4:26b → clean SQL
  │
  ▼
execute_sql       → run on PostgreSQL → on error: inject error into state
  │
  ├── error + retry_count < 3 ──► generate_sql  (self-correcting loop)
  │
  └── success / max retries ──►
                                format_answer → gemma4:26b → natural language response
                                  │
                                 END
```

---

## ✨ Features

- **100% local** — no OpenAI key, no cloud, no data leaves your machines
- **Self-correcting SQL** — LangGraph retry loop automatically fixes SQL errors (up to 3 attempts)
- **Semantic schema retrieval** — PGVector finds the most relevant table definitions and join patterns for each question
- **Rich terminal UI** — formatted tables, answer panels, debug mode to inspect generated SQL
- **Dockerised database** — pgvector/pg18 container with persistent volume, zero host install
- **Hot-swappable LLM** — change `OLLAMA_LLM_MODEL` in `.env` to switch models instantly

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| LLM Orchestration | LangGraph 0.2+, LangChain 0.3+ |
| Local LLM | Ollama — gemma4:26b |
| Embedding Model | Ollama — nomic-embed-text (768-dim) |
| Vector Store | PGVector (langchain-postgres) |
| Database | PostgreSQL 18 (pgvector/pgvector:pg18 Docker image) |
| Container | Docker Compose |
| Terminal UI | Rich |
| OS (app) | Linux (RHEL/CentOS 9) |
| OS (LLM) | Windows 11 |

---

## 📁 Project Structure

```
/u01/nl_sql/
├── aidb/
│   └── docker-compose.yml          # pgvector Docker setup
│
└── banking_rag/
    ├── .env                         # environment variables (not committed)
    ├── .env.example                 # template
    ├── requirements.txt
    ├── main.py                      # entry point
    │
    ├── sql/
    │   ├── 01_schema.sql            # customers, accounts, transactions + indexes
    │   └── 02_seed_data.sql         # 10 customers, 16 accounts, 17 transactions
    │
    ├── src/
    │   ├── __init__.py
    │   ├── config.py                # env-driven configuration
    │   ├── graph.py                 # LangGraph agent (4 nodes + retry logic)
    │   └── cli.py                   # Rich terminal interface
    │
    └── scripts/
        └── ingest_schema.py         # one-time schema embedding into PGVector
```

---

## ⚙️ Prerequisites

### Windows Machine (LLM host)

1. Install [Ollama for Windows](https://ollama.com/download/windows)
2. In Ollama Settings → enable **"Expose Ollama to the network"**
3. Open firewall port 11434:
   ```powershell
   netsh advfirewall firewall add rule name="Ollama" dir=in action=allow protocol=TCP localport=11434
   ```
4. Pull required models:
   ```powershell
   ollama pull gemma4:26b
   ollama pull nomic-embed-text
   ```

### Linux Machine (app host)

- Python 3.13
- Docker + Docker Compose
- Network access to the Windows machine on port 11434

---

## 🚀 Quick Start

### 1. Start the database

```bash
mkdir -p /u01/nl_sql/aidb && cd /u01/nl_sql/aidb

cat << 'EOF' > docker-compose.yml
services:
  pg-vector-db:
    image: pgvector/pgvector:pg18
    container_name: pg-vector-db
    restart: always
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: banking_db
    ports:
      - "5432:5432"
    volumes:
      - pgvector_data:/var/lib/postgresql

volumes:
  pgvector_data:
EOF

docker compose up -d
```

### 2. Load the banking schema and data

```bash
cd /u01/nl_sql/banking_rag

docker exec -i pg-vector-db psql -U admin -d banking_db < sql/01_schema.sql
docker exec -i pg-vector-db psql -U admin -d banking_db < sql/02_seed_data.sql
```

### 3. Set up Python environment

```bash
cd /u01/nl_sql/banking_rag
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
vi .env   # fill in your values — see Configuration section below
```

### 5. Embed schema definitions into PGVector

```bash
python3.13 -m scripts.ingest_schema
```

### 6. Launch the terminal chatbot

```bash
python main.py
```

---

## 💬 Usage

```
You › How many customers do we have?
You › Which customer has the highest total balance?
You › Show all debit transactions in the last 30 days
You › What is the total balance breakdown by account type?
You › List all frozen accounts with customer names
You › Who made the largest single transaction?
You › debug         ← toggles SQL query display on/off
You › quit          ← exits
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill in your values:

```env
# PostgreSQL (Docker container)
PG_HOST=localhost          # or container host IP
PG_PORT=5432
PG_DATABASE=banking_db
PG_USER=admin
PG_PASSWORD=secret

# Ollama (Windows machine)
OLLAMA_BASE_URL=http://192.168.0.102:11434
OLLAMA_LLM_MODEL=gemma4:26b
OLLAMA_EMBED_MODEL=nomic-embed-text
```

| Variable | Description | Default |
|---|---|---|
| `PG_HOST` | PostgreSQL host | `localhost` |
| `PG_PORT` | PostgreSQL port | `5432` |
| `PG_DATABASE` | Database name | `banking_db` |
| `PG_USER` | DB user | `admin` |
| `PG_PASSWORD` | DB password | — |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_LLM_MODEL` | LLM for SQL generation | `gemma4:26b` |
| `OLLAMA_EMBED_MODEL` | Model for embeddings | `nomic-embed-text` |

---

## 🔍 How It Works

### 1. Schema stored as semantic documents
Table definitions, join patterns, and report templates are embedded as natural language documents in PGVector. This means the system understands concepts like *"total balance per customer"* even though those exact words aren't in your SQL schema.

### 2. Retrieval-augmented SQL generation
When you ask a question, it is embedded and the top-5 most semantically relevant schema documents are retrieved. These are injected directly into the LLM prompt — the model sees the exact column names, data types, and join keys it needs.

### 3. Self-correcting retry loop
If the generated SQL fails on PostgreSQL, the error message is fed back into the prompt and the LLM generates a corrected query. This loop runs up to 3 times before gracefully reporting failure.

### 4. Natural language formatting
After a successful query, the raw results are sent back to the LLM to produce a concise, human-readable summary of the findings.

---

## 🗄️ Database Schema

```
customers                    accounts                      transactions
─────────────────────        ─────────────────────────     ─────────────────────────────
customer_id  PK              account_id     PK             transaction_id   PK
full_name                    customer_id    FK ──────────► account_id       FK
email                        account_number                transaction_type
phone                        account_type                  amount
address                      balance                       description
created_at                   status                        transaction_date
                             opened_at                     balance_after
```

**Seed data:** 10 customers · 16 accounts (savings/checking/loan) · 17 transactions

---

## 🛠️ Troubleshooting

**Ollama not reachable from Linux:**
```bash
curl http://<windows-ip>:11434/api/tags
# If this fails: check "Expose Ollama to the network" toggle in Ollama settings
# and verify Windows Firewall allows port 11434
```

**Embedding dimension mismatch:**
```bash
# Verify nomic-embed-text returns 768 dims
python3.13 -c "
from langchain_ollama import OllamaEmbeddings
e = OllamaEmbeddings(base_url='http://192.168.0.102:11434', model='nomic-embed-text')
print(len(e.embed_query('test')))   # should print: 768
"
```

**Re-run schema ingestion after code changes:**
```bash
python3.13 -m scripts.ingest_schema   # safe to re-run, deletes and recreates collection
```

**Inspect vector store contents:**
```bash
docker exec -it pg-vector-db psql -U admin -d banking_db -c "
SELECT cmetadata->>'name' AS name,
       cmetadata->>'type' AS type,
       SUBSTRING(document, 1, 60) AS preview
FROM langchain_pg_embedding;"
```

---

## 📈 Extending the Project

- **Add more schema docs** — edit `scripts/ingest_schema.py` and add `Document()` entries for new tables or reports, then re-run ingestion
- **Switch models** — change `OLLAMA_LLM_MODEL` in `.env` (e.g. `llama3.1:8b` for faster responses)
- **Add authentication** — wrap `cli.py` with a login prompt before allowing queries
- **REST API** — replace `cli.py` with a FastAPI app that exposes the LangGraph pipeline as an HTTP endpoint
- **Multi-database support** — parameterise `PG_DATABASE` and ingest separate schema collections per database

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- [LangChain](https://langchain.com) / [LangGraph](https://langchain-ai.github.io/langgraph/) for the orchestration framework
- [Ollama](https://ollama.com) for making local LLM inference approachable
- [pgvector](https://github.com/pgvector/pgvector) for native PostgreSQL vector search
- [Google Gemma 4](https://ai.google.dev/gemma) for the open-weight LLM

---

<p align="center">Built with ❤️ in Dhaka, Bangladesh</p>
