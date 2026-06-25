# Log Diagnosis Agent

## Problem
Routers and network devices generate thousands of logs daily. Most are noise.
Finding real failures requires manually searching documentation, cross-referencing
error codes, and deciding whether an issue is known or anomalous. That process
is slow and doesn't scale.

## Solution
An agentic AI pipeline that ingests raw logs, filters noise before any LLM call,
classifies issues, retrieves relevant context from documentation, and returns a
structured diagnosis engineers can act on.

## Architecture

```mermaid
graph TD
    A[Mock Logs]
    B(FastAPI API)
    C{LangGraph Agent}

    D[Noise Detection]
    E[Issue Classification]
    F[RAG Retrieval: pgvector]
    G[Diagnosis Generation]

    H[/JSON Diagnosis/]

    A --> B
    B --> C

    C --> D
    C --> E
    C --> F
    C --> G

    D --> H
    E --> H
    F --> H
    G --> H

    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px;
    classDef agent fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef output fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;

    class C agent;
    class H output;
```

## Stack
Python, FastAPI, LangGraph, HuggingFace Transformers, PostgreSQL, pgvector,
Docker, OpenAI API

## Sample Output
```json
{
  "device_id": "RTR-X99",
  "severity": "Critical",
  "error": "Connection Timeout on eth0",
  "anomaly_status": "True Anomaly",
  "diagnosis": "High probability of ISP outage based on symptom cluster.",
  "context": "Manual Pg 45: If error persists > 5 mins, check ISP gateway.",
  "recommended_action": "Ping ISP Gateway IP"
}
```
