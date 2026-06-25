"""FastAPI application entry point."""

from fastapi import FastAPI

from app import __version__
from app.models import AnalyzeRequest, AnalyzeResponse, HealthResponse

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
    """Accept a log payload and return a placeholder analysis result."""
    return AnalyzeResponse(
        device_id=request.device_id,
        status="received",
        message="Log received for analysis. AI pipeline not yet implemented.",
    )
