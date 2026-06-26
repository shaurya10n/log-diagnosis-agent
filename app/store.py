"""In-memory store for analysis history and dashboard stats."""

from collections import deque
from datetime import datetime, timezone
from typing import Deque, List

from app.models import AnalyzeResponse, DashboardStats, LogEntry

_MAX_LOGS = 20
_history: Deque[LogEntry] = deque(maxlen=_MAX_LOGS)


def record_analysis(log: str, response: AnalyzeResponse) -> LogEntry:
    """Store an analysis result and return the log entry."""
    entry = LogEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        device_id=response.device_id,
        log=log,
        category=response.category,
        severity=response.severity,
        anomaly_status=response.anomaly_status,
        known_fix=response.known_fix,
        rag_context=response.rag_context,
        diagnosis=response.diagnosis,
        recommended_action=response.recommended_action,
    )
    _history.appendleft(entry)
    return entry


def get_logs() -> List[LogEntry]:
    """Return the last 20 analysis results (newest first)."""
    return list(_history)


def get_stats() -> DashboardStats:
    """Compute dashboard counters from stored analyses."""
    entries = list(_history)
    return DashboardStats(
        total_analyzed=len(entries),
        noise_filtered=sum(1 for e in entries if e.category == "NOISE"),
        known_issues=sum(1 for e in entries if e.anomaly_status == "KNOWN_ISSUE"),
        true_anomalies=sum(1 for e in entries if e.anomaly_status == "TRUE_ANOMALY"),
    )
