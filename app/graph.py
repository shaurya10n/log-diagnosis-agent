"""LangGraph workflow definition for the incident diagnosis pipeline."""

from langgraph.graph import StateGraph


def build_graph() -> StateGraph:
    """Construct and return the diagnosis agent graph.

    Pipeline stages to wire: noise filter → classifier → anomaly detection
    → RAG retrieval → diagnosis writer.
    """
    raise NotImplementedError("Graph wiring will be implemented in a later iteration.")
