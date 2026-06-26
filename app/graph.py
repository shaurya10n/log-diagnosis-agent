"""LangGraph workflow definition for the incident diagnosis pipeline."""

from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.agents.anomaly_detector import detect_anomaly
from app.agents.classifier import classify_log
from app.agents.rag_agent import retrieve_rag_context
from app.state import GraphState

__all__ = ["GraphState", "build_graph"]


def noise_filter(state: GraphState) -> dict[str, bool]:
    """Stop the pipeline early when the log is classified as noise."""
    if state["category"] == "NOISE":
        return {"should_continue": False}
    return {"should_continue": True}


def diagnosis(state: GraphState) -> dict:
    """Placeholder for downstream diagnosis writer."""
    return {}


def _route_after_classify(state: GraphState) -> Literal["end", "noise_filter"]:
    if state["category"] == "NOISE":
        return "end"
    return "noise_filter"


def _route_after_anomaly_check(state: GraphState) -> Literal["end", "rag_retrieval"]:
    if state["anomaly_status"] == "KNOWN_ISSUE":
        return "end"
    return "rag_retrieval"


def build_graph():
    """Construct and compile the diagnosis agent graph."""
    graph = StateGraph(GraphState)

    graph.add_node("classify_log", classify_log)
    graph.add_node("noise_filter", noise_filter)
    graph.add_node("anomaly_check", detect_anomaly)
    graph.add_node("rag_retrieval", retrieve_rag_context)
    graph.add_node("diagnosis", diagnosis)

    graph.add_edge(START, "classify_log")
    graph.add_conditional_edges(
        "classify_log",
        _route_after_classify,
        {"end": END, "noise_filter": "noise_filter"},
    )
    graph.add_edge("noise_filter", "anomaly_check")
    graph.add_conditional_edges(
        "anomaly_check",
        _route_after_anomaly_check,
        {"end": END, "rag_retrieval": "rag_retrieval"},
    )
    graph.add_edge("rag_retrieval", "diagnosis")
    graph.add_edge("diagnosis", END)

    return graph.compile()
