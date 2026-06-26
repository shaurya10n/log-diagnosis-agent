"""LangGraph workflow definition for the incident diagnosis pipeline."""

from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.agents.anomaly_detector import detect_anomaly
from app.agents.classifier import classify_log
from app.agents.diagnosis_writer import write_diagnosis
from app.agents.rag_agent import retrieve_rag_context
from app.state import GraphState

__all__ = ["GraphState", "build_graph"]


def _route_after_classify(state: GraphState) -> Literal["end", "anomaly_check"]:
    if state["category"] == "NOISE":
        return "end"
    return "anomaly_check"


def _route_after_anomaly_check(state: GraphState) -> Literal["end", "rag_retrieval"]:
    if state["anomaly_status"] == "KNOWN_ISSUE":
        return "end"
    return "rag_retrieval"


def build_graph():
    """Construct and compile the diagnosis agent graph."""
    graph = StateGraph(GraphState)

    graph.add_node("classify_log", classify_log)
    graph.add_node("anomaly_check", detect_anomaly)
    graph.add_node("rag_retrieval", retrieve_rag_context)
    graph.add_node("diagnosis", write_diagnosis)

    graph.add_edge(START, "classify_log")
    graph.add_conditional_edges(
        "classify_log",
        _route_after_classify,
        {"end": END, "anomaly_check": "anomaly_check"},
    )
    graph.add_conditional_edges(
        "anomaly_check",
        _route_after_anomaly_check,
        {"end": END, "rag_retrieval": "rag_retrieval"},
    )
    graph.add_edge("rag_retrieval", "diagnosis")
    graph.add_edge("diagnosis", END)

    return graph.compile()
