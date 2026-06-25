"""FastAPI application entry point."""

from fastapi import FastAPI

from app import __version__

app = FastAPI(
    title="AI Incident Diagnosis Agent",
    description="Agentic pipeline for log ingestion, classification, and diagnosis.",
    version=__version__,
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe for orchestrators and load balancers."""
    return {"status": "ok"}
