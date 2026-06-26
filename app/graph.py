"""LangGraph workflow definition for the incident diagnosis pipeline."""

from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.agents.classifier import classify_log
from app.state import GraphState

__all__ = ["GraphState", "build_graph"]


def noise_filter(state: GraphState) -> dict[str, bool]:
    """Stop the pipeline early when the log is classified as noise."""
    if state["category"] == "NOISE":
        return {"should_continue": False}
    return {"should_continue": True}


def anomaly_check(state: GraphState) -> dict:
    """Placeholder for downstream anomaly detection."""
    return {}


def _route_after_classify(state: GraphState) -> Literal["end", "noise_filter"]:
    if state["category"] == "NOISE":
        return "end"
    return "noise_filter"


def build_graph():
    """Construct and compile the diagnosis agent graph."""
    graph = StateGraph(GraphState)

    graph.add_node("classify_log", classify_log)
    graph.add_node("noise_filter", noise_filter)
    graph.add_node("anomaly_check", anomaly_check)

    graph.add_edge(START, "classify_log")
    graph.add_conditional_edges(
        "classify_log",
        _route_after_classify,
        {"end": END, "noise_filter": "noise_filter"},
    )
    graph.add_edge("noise_filter", "anomaly_check")
    graph.add_edge("anomaly_check", END)

    return graph.compile()
