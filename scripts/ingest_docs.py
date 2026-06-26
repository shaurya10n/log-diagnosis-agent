#!/usr/bin/env python3
"""Load router manual chunks from JSON and ingest into pgvector."""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.rag.retriever import create_table, ingest_docs  # noqa: E402


def main() -> None:
    docs_path = PROJECT_ROOT / "data" / "router_docs.json"
    with docs_path.open(encoding="utf-8") as f:
        docs = json.load(f)

    create_table()
    inserted = ingest_docs(docs)
    print(f"Ingested {inserted} new document(s) from {docs_path} ({len(docs)} total in file).")


if __name__ == "__main__":
    main()
