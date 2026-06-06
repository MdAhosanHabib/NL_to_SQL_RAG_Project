"""
LangGraph agent with 4 nodes:
  retrieve_schema → generate_sql → execute_sql → format_answer
with a self-correcting retry loop on SQL errors (max 3 attempts).
"""
import re
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import TypedDict, Optional

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_postgres import PGVector
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

from .config import (
    PG_DSN, PG_VECTOR_URL,
    OLLAMA_BASE_URL, OLLAMA_LLM_MODEL, OLLAMA_EMBED_MODEL,
    VECTOR_COLLECTION,
)

# ── Shared singletons ─────────────────────────────────────────────────────────
_llm = None
_vector_store = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOllama(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_LLM_MODEL,
            temperature=0,
        )
    return _llm

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        embeddings = OllamaEmbeddings(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_EMBED_MODEL,
        )
        _vector_store = PGVector(
            embeddings=embeddings,
            collection_name=VECTOR_COLLECTION,
            connection=PG_VECTOR_URL,
        )
    return _vector_store


# ── State ─────────────────────────────────────────────────────────────────────
class BankingRAGState(TypedDict):
    question:       str
    schema_context: str
    generated_sql:  str
    error_feedback: Optional[str]
    query_result:   Optional[list]
    execution_error: Optional[str]
    retry_count:    int
    final_answer:   str


# ── Node 1: retrieve relevant schema docs ────────────────────────────────────
def retrieve_schema(state: BankingRAGState) -> dict:
    docs = get_vector_store().similarity_search(state["question"], k=5)
    context = "\n\n---\n\n".join(d.page_content for d in docs)
    return {"schema_context": context}


# ── Node 2: generate SQL via LLM ─────────────────────────────────────────────
def generate_sql(state: BankingRAGState) -> dict:
    error_note = ""
    if state.get("error_feedback"):
        error_note = (
            f"\n\nYour previous SQL failed with this error:\n"
            f"  {state['error_feedback']}\n"
            f"Fix the query accordingly."
        )

    system = f"""You are a PostgreSQL SQL expert for a banking database.
Output ONLY the raw SQL query — no markdown fences, no explanation.

Rules:
- Use only tables/columns present in the schema context below
- Always alias tables (c for customers, a for accounts, t for transactions)
- Use COALESCE for nullable columns in aggregations
- Default LIMIT 50 unless the question asks for all
- Use proper PostgreSQL syntax (NUMERIC not FLOAT, DATE_TRUNC, etc.)
{error_note}

Schema context:
{state["schema_context"]}"""

    response = get_llm().invoke([
        SystemMessage(content=system),
        HumanMessage(content=f"Question: {state['question']}\n\nSQL:"),
    ])

    sql = response.content.strip()
    # Strip accidental markdown fences
    sql = re.sub(r"```sql\s*", "", sql)
    sql = re.sub(r"```\s*", "", sql)
    sql = sql.strip().rstrip(";") + ";"   # ensure single trailing semicolon

    return {
        "generated_sql":  sql,
        "execution_error": None,   # clear previous error
        "error_feedback":  None,
    }


# ── Node 3: execute SQL on PostgreSQL ────────────────────────────────────────
def execute_sql(state: BankingRAGState) -> dict:
    try:
        conn = psycopg2.connect(PG_DSN)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(state["generated_sql"])
            rows = cur.fetchall()
        conn.close()
        return {
            "query_result":   [dict(r) for r in rows],
            "execution_error": None,
        }
    except Exception as exc:
        return {
            "query_result":    None,
            "execution_error": str(exc),
            "error_feedback":  str(exc),
            "retry_count":     state.get("retry_count", 0) + 1,
        }


# ── Conditional edge: retry or proceed ───────────────────────────────────────
def should_retry(state: BankingRAGState) -> str:
    if state.get("execution_error") and state.get("retry_count", 0) < 3:
        return "generate_sql"
    return "format_answer"


# ── Node 4: format natural-language answer ───────────────────────────────────
def format_answer(state: BankingRAGState) -> dict:
    if state.get("execution_error") and not state.get("query_result"):
        answer = (
            f"Could not answer after {state.get('retry_count', 0)} attempt(s).\n"
            f"Last error: {state['execution_error']}"
        )
        return {"final_answer": answer}

    result_preview = json.dumps(
        state["query_result"][:15], indent=2, default=str
    )

    response = get_llm().invoke([
        HumanMessage(content=(
            f"Question: {state['question']}\n\n"
            f"SQL used:\n{state['generated_sql']}\n\n"
            f"Result ({len(state['query_result'])} rows):\n{result_preview}\n\n"
            "Give a clear, concise answer. Include specific numbers. "
            "If there are many rows, summarise the key findings."
        ))
    ])

    return {"final_answer": response.content.strip()}


# ── Build and compile graph ───────────────────────────────────────────────────
def build_graph():
    g = StateGraph(BankingRAGState)

    g.add_node("retrieve_schema", retrieve_schema)
    g.add_node("generate_sql",    generate_sql)
    g.add_node("execute_sql",     execute_sql)
    g.add_node("format_answer",   format_answer)

    g.add_edge(START,              "retrieve_schema")
    g.add_edge("retrieve_schema",  "generate_sql")
    g.add_edge("generate_sql",     "execute_sql")

    g.add_conditional_edges(
        "execute_sql",
        should_retry,
        {"generate_sql": "generate_sql", "format_answer": "format_answer"},
    )

    g.add_edge("format_answer", END)

    return g.compile()

