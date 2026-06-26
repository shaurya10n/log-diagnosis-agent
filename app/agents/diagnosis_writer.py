"""Diagnosis writer: generates engineer-readable diagnosis via Groq LLM."""

import json
import os
import re
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.state import GraphState

load_dotenv()

DIAGNOSIS_SYSTEM_PROMPT = """You are an expert network engineer. Given a router log, anomaly classification, and relevant documentation context, write a concise diagnosis and recommended action.

Return only JSON with keys: "diagnosis" and "recommended_action". No markdown, no explanation outside the JSON."""

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


def _parse_diagnosis_response(content: str) -> Dict[str, str]:
    """Extract diagnosis and recommended_action JSON from the LLM response."""
    text = content.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    else:
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            text = brace_match.group(0)

    parsed: Dict[str, Any] = json.loads(text)
    return {
        "diagnosis": str(parsed["diagnosis"]),
        "recommended_action": str(parsed["recommended_action"]),
    }


def _format_context(rag_context: list[str]) -> str:
    if not rag_context:
        return "- No manual context retrieved."
    return "\n".join(f"- {chunk}" for chunk in rag_context)


def write_diagnosis(state: GraphState) -> Dict[str, str]:
    """Generate diagnosis and recommended action from log, classification, and RAG context."""
    user_prompt = (
        f"Log: {state['raw_log']}\n"
        f"Category: {state['category']}\n"
        f"Severity: {state['severity']}\n"
        f"Anomaly Status: {state['anomaly_status']}\n"
        f"Context from manuals:\n{_format_context(state['rag_context'])}"
    )

    response = _get_model().invoke(
        [
            SystemMessage(content=DIAGNOSIS_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )
    result = _parse_diagnosis_response(str(response.content))
    return {
        "diagnosis": result["diagnosis"],
        "recommended_action": result["recommended_action"],
    }
