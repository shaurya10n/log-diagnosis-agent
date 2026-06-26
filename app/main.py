"""FastAPI application entry point."""

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app import __version__
from app.graph import build_graph
from app.models import AnalyzeRequest, AnalyzeResponse, HealthResponse

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
    return AnalyzeResponse(
        device_id=result["device_id"],
        category=result["category"],
        severity=result["severity"],
        anomaly_status=result["anomaly_status"],
        known_fix=result.get("known_fix"),
        rag_context=result.get("rag_context", []),
        diagnosis=result.get("diagnosis", ""),
        recommended_action=result.get("recommended_action", ""),
    )
