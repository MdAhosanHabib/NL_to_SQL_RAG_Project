import os
from dotenv import load_dotenv

load_dotenv()

PG_HOST     = os.getenv("PG_HOST", "192.168.0.105")
PG_PORT     = os.getenv("PG_PORT", "5432")
PG_DATABASE = os.getenv("PG_DATABASE", "banking_db")
PG_USER     = os.getenv("PG_USER", "admin")
PG_PASSWORD = os.getenv("PG_PASSWORD", "secret")

# psycopg2 DSN for direct queries
PG_DSN = (
    f"host={PG_HOST} port={PG_PORT} "
    f"dbname={PG_DATABASE} user={PG_USER} password={PG_PASSWORD}"
)

# SQLAlchemy URL for langchain-postgres PGVector
PG_VECTOR_URL = (
    f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}"
    f"@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
)

OLLAMA_BASE_URL   = os.getenv("OLLAMA_BASE_URL", "http://192.168.0.102:11434")
OLLAMA_LLM_MODEL  = os.getenv("OLLAMA_LLM_MODEL", "gemma4:26b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

VECTOR_COLLECTION = "banking_schema"
