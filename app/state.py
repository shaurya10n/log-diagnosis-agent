"""LangGraph state schema for the diagnosis pipeline."""

from typing import TypedDict


class GraphState(TypedDict):
    """Shared state passed between graph nodes."""

    device_id: str
    raw_log: str
    category: str
    severity: str
    should_continue: bool
