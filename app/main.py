"""FastAPI application entry point."""

from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app import __version__
from app.graph import build_graph
from app.models import (
    AnalyzeRequest,
    AnalyzeResponse,
    DashboardStats,
    HealthResponse,
    LogEntry,
)
from app.store import get_logs, get_stats, record_analysis

_graph = build_graph()

app = FastAPI(
    title="AI Incident Diagnosis Agent",
    description="Agentic pipeline for log ingestion, classification, and diagnosis.",
    version=__version__,
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness probe for orchestrators and load balancers."""
    return HealthResponse(status="ok")


@app.get("/logs", response_model=List[LogEntry])
async def logs() -> List[LogEntry]:
    """Return the last 20 analysis results stored in memory."""
    return get_logs()


@app.get("/dashboard/stats", response_model=DashboardStats)
async def dashboard_stats() -> DashboardStats:
    """Return aggregate analysis counters from in-memory history."""
    return get_stats()


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Accept a log payload, run the diagnosis graph, and return the final state."""
    result = _graph.invoke(
        {
            "device_id": request.device_id,
            "raw_log": request.log,
            "category": "",
            "severity": "",
            "should_continue": True,
            "anomaly_status": "",
            "known_fix": None,
            "rag_context": [],
            "diagnosis": "",
            "recommended_action": "",
        }
    )
    response = AnalyzeResponse(
        device_id=result["device_id"],
        category=result["category"],
        severity=result["severity"],
        anomaly_status=result["anomaly_status"],
        known_fix=result.get("known_fix"),
        rag_context=result.get("rag_context", []),
        diagnosis=result.get("diagnosis", ""),
        recommended_action=result.get("recommended_action", ""),
    )
    record_analysis(request.log, response)
    return response
