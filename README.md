# AI Incident Diagnosis Agent

An agentic pipeline that ingests raw router logs, filters noise, classifies severity, detects known vs. anomalous issues, retrieves relevant manual context via RAG, and returns an engineer-readable diagnosis with recommended actions.

Built with FastAPI, LangGraph, Groq, sentence-transformers, and PostgreSQL/pgvector.

## Architecture

```
POST /analyze
    │
    ▼
classify_log ──(NOISE)──────────────────────────────► END
    │
    ▼
noise_filter
    │
    ▼
anomaly_check ──(KNOWN_ISSUE + known_fix)───────────► END
    │
    ▼
rag_retrieval (pgvector similarity search)
    │
    ▼
diagnosis (Groq LLM writes diagnosis + action)
    │
    ▼
   END
```

## Run locally with Docker

1. Copy environment variables and add your Groq API key:

```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY
```

2. Start the stack:

```bash
make run
```

3. Ingest router manual documents into pgvector (first time only):

```bash
make ingest
```

4. Verify the service:

```bash
curl http://localhost:8000/health
```

## Example: analyze a log

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "router-01",
    "log": "BGP neighbor 10.0.0.1 down, hold timer expired"
  }'
```

Other endpoints:

- `GET /logs` — last 20 analysis results (in-memory)
- `GET /dashboard/stats` — aggregate counts (noise, known issues, true anomalies)

## Makefile

| Command       | Description                          |
|---------------|--------------------------------------|
| `make run`    | Build and start app + Postgres       |
| `make ingest` | Load `data/router_docs.json` into DB |
| `make test`   | Placeholder for future tests         |
