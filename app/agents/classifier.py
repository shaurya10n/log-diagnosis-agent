"""Classifier agent: categorizes router logs via Groq LLM."""

import json
import os
import re
from typing import Any, Dict, Optional, Union

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.state import GraphState

load_dotenv()

CLASSIFIER_SYSTEM_PROMPT = """You are a network operations classifier for enterprise router logs.

Given a single router log message, classify it into exactly one category and assign a severity level.

Categories:
- NOISE: Routine, expected, or low-value messages (heartbeats, link state up/down on stable links, debug chatter, duplicate suppressions).
- KNOWN_ISSUE: Recognizable, documented failure patterns (auth failures, DHCP timeouts, BGP hold-time warnings, interface flaps with known root cause).
- ANOMALY: Unexpected or suspicious behavior that may indicate an incident (sudden error spikes, unknown protocol errors, config drift, security-relevant events).

Severity levels:
- LOW: Informational; no service impact.
- MEDIUM: Degraded performance or intermittent failures; monitor closely.
- HIGH: Significant impact to connectivity or services; needs prompt attention.
- CRITICAL: Outage, data loss risk, or active security threat; immediate escalation.

Respond with ONLY valid JSON — no markdown, no explanation — using exactly these keys:
{"category": "<NOISE|KNOWN_ISSUE|ANOMALY>", "severity": "<LOW|MEDIUM|HIGH|CRITICAL>"}"""

_MODEL: Optional[ChatGroq] = None


def _get_model() -> ChatGroq:
    global _MODEL
    if _MODEL is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY environment variable is not set")
        _MODEL = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            api_key=api_key,
            temperature=0,
        )
    return _MODEL


def _parse_classifier_response(content: str) -> dict[str, str]:
    """Extract category and severity JSON from the LLM response."""
    text = content.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    else:
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            text = brace_match.group(0)

    parsed: dict[str, Any] = json.loads(text)
    category = str(parsed["category"]).upper()
    severity = str(parsed["severity"]).upper()

    valid_categories = {"NOISE", "KNOWN_ISSUE", "ANOMALY"}
    valid_severities = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    if category not in valid_categories:
        raise ValueError(f"Invalid category: {category}")
    if severity not in valid_severities:
        raise ValueError(f"Invalid severity: {severity}")

    return {"category": category, "severity": severity}


def classify_log(state: GraphState) -> Dict[str, Union[str, bool]]:
    """Classify a router log message and update graph state."""
    response = _get_model().invoke(
        [
            SystemMessage(content=CLASSIFIER_SYSTEM_PROMPT),
            HumanMessage(
                content=f"Device ID: {state['device_id']}\n\nLog message:\n{state['raw_log']}"
            ),
        ]
    )
    result = _parse_classifier_response(str(response.content))
    return {
        "category": result["category"],
        "severity": result["severity"],
        "should_continue": result["category"] != "NOISE",
    }
