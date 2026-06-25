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
    A[Mock Logs] --> B[FastAPI]
    B --> C[LangGraph Agent]

    C --> D[1. Noise Filter]
    D -->|98% dropped| Z[/Discarded/]
    D -->|passes| E[2. Classifier]

    E --> F[3. Anomaly Detection]
    F -->|known issue| G[Stored Fix]
    F -->|true anomaly| H[4. RAG Retrieval\npgvector]

    G --> I[/JSON Diagnosis/]
    H --> J[5. Diagnosis Writer]
    J --> I
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
