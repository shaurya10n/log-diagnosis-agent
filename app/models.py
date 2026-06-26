"""Pydantic schemas for API requests and responses."""

from typing import Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., examples=["ok"])


class AnalyzeRequest(BaseModel):
    """Incoming log payload for analysis."""

    device_id: str = Field(..., min_length=1, description="Identifier of the device that produced the log.")
    log: str = Field(..., min_length=1, description="Raw log text to analyze.")


class AnalyzeResponse(BaseModel):
    """Analysis result returned after running the LangGraph pipeline."""

    device_id: str
    raw_log: str
    category: str
    severity: str
    should_continue: bool
    anomaly_status: str
    known_fix: Optional[str] = None
