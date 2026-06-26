"""PostgreSQL + pgvector similarity search for router documentation."""

import os
from typing import Any, Dict, List

import psycopg2
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector
from psycopg2.extras import RealDictCursor

from app.rag.embedder import embed_documents, embed_text

load_dotenv()


def _get_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    conn = psycopg2.connect(database_url)
    try:
        register_vector(conn)
    except psycopg2.ProgrammingError:
        conn.close()
        conn = psycopg2.connect(database_url)
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()
        register_vector(conn)
    return conn


def create_table() -> None:
    """Create the router_docs table with pgvector embedding column."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")

    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS router_docs (
                    id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector(384)
                )
                """
            )
        conn.commit()
    finally:
        conn.close()


def ingest_docs(docs: List[Dict[str, Any]]) -> int:
    """Embed and insert documents, skipping any that already exist."""
    embedded = embed_documents(docs)
    inserted = 0

    with _get_connection() as conn:
        with conn.cursor() as cur:
            for doc in embedded:
                cur.execute("SELECT 1 FROM router_docs WHERE id = %s", (doc["id"],))
                if cur.fetchone():
                    continue
                cur.execute(
                    """
                    INSERT INTO router_docs (id, source, content, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (doc["id"], doc["source"], doc["content"], doc["embedding"]),
                )
                inserted += 1
        conn.commit()

    return inserted


def retrieve(query: str, top_k: int = 3) -> List[Dict[str, str]]:
    """Return the top-k most similar documents for a query string."""
    query_embedding = embed_text(query)

    with _get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT source, content
                FROM router_docs
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (query_embedding, top_k),
            )
            rows = cur.fetchall()

    return [{"source": row["source"], "content": row["content"]} for row in rows]
