"""Pydantic schemas for API requests, responses, and agent state."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., examples=["ok"])


class DiagnosisRequest(BaseModel):
    """Incoming log or incident payload for diagnosis."""

    device_id: str
    log_lines: list[str] = Field(default_factory=list)


class DiagnosisResponse(BaseModel):
    """Structured diagnosis returned to the caller."""

    device_id: str
    severity: str
    error: str
    anomaly_status: str
    diagnosis: str
    context: str
    recommended_action: str
