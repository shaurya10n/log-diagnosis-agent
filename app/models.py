"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., examples=["ok"])


class AnalyzeRequest(BaseModel):
    """Incoming log payload for analysis."""

    device_id: str = Field(..., min_length=1, description="Identifier of the device that produced the log.")
    log: str = Field(..., min_length=1, description="Raw log text to analyze.")


class AnalyzeResponse(BaseModel):
    """Placeholder analysis response until AI pipeline is wired."""

    device_id: str
    status: str
    message: str
