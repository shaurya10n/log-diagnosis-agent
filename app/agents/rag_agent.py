"""RAG agent: retrieves relevant router manual context for a log message."""

from typing import Dict, List

from app.rag.retriever import retrieve
from app.state import GraphState


def retrieve_rag_context(state: GraphState) -> Dict[str, List[str]]:
    """Retrieve top-k manual chunks and add them to graph state."""
    results = retrieve(state["raw_log"], top_k=3)
    rag_context = [f"[{doc['source']}] {doc['content']}" for doc in results]
    return {"rag_context": rag_context}
