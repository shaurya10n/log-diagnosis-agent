"""Pydantic schemas for API requests and responses."""

from typing import List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., examples=["ok"])


class AnalyzeRequest(BaseModel):
    """Incoming log payload for analysis."""

    device_id: str = Field(..., min_length=1, description="Identifier of the device that produced the log.")
    log: str = Field(..., min_length=1, description="Raw log text to analyze.")


class AnalyzeResponse(BaseModel):
    """Full analysis result returned after running the LangGraph pipeline."""

    device_id: str
    category: str
    severity: str
    anomaly_status: str
    known_fix: Optional[str] = None
    rag_context: List[str] = []
    diagnosis: str = ""
    recommended_action: str = ""


class LogEntry(BaseModel):
    """A stored analysis result with metadata."""

    timestamp: str
    device_id: str
    log: str
    category: str
    severity: str
    anomaly_status: str
    known_fix: Optional[str] = None
    rag_context: List[str] = []
    diagnosis: str = ""
    recommended_action: str = ""


class DashboardStats(BaseModel):
    """Aggregate counters for the analysis dashboard."""

    total_analyzed: int
    noise_filtered: int
    known_issues: int
    true_anomalies: int


# Alias for clarity in documentation and downstream consumers.
AnalysisResponse = AnalyzeResponse
