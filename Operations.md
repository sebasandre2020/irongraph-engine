# Operations & Production Runbook: IronGraph-Engine

**Status**: Operational guide and local engineering runbook. [Index](Index.md) · [Architecture](Architecture.md)

---

## 1. Local Development Runbook

### Prerequisites
- Python 3.12+ installed
- Docker & Docker Compose v2+
- Git

### Quickstart Execution Steps
```powershell
# 1. Initialize Python environment
cd C:\Repositories\GHProjects\irongraph-engine
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt

# 2. Run automated scaffold and integrity checks
python scripts/validate_scaffold.py

# 3. Environment configuration
Copy-Item .env.example .env

# 4. Launch dependent infrastructure
docker compose config --quiet
docker compose up -d postgres redis qdrant

# 5. Verify database initialization
docker compose exec postgres psql -U irongraph -d irongraph_db -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"

# 6. Verify Qdrant Vector Engine
curl http://localhost:6333/collections

# 7. Teardown
docker compose down
```

---

## 2. Environment Configuration Matrix

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `development` | Deployment tier: `development`, `staging`, `production` |
| `PORT` | `8000` | Application HTTP listening port |
| `DATABASE_URL` | `postgresql+asyncpg://irongraph:irongraph_secret@localhost:5432/irongraph_db` | Primary relational & exercise graph DSN |
| `REDIS_URL` | `redis://localhost:6379/0` | Active lifter session & graph cache DSN |
| `QDRANT_HOST` | `localhost` | Qdrant vector database hostname |
| `QDRANT_PORT` | `6333` | Qdrant REST API port |
| `LLM_PRIMARY_PROVIDER`| `anthropic` | Primary foundation model: `anthropic`, `openai`, `bedrock` |
| `ANTHROPIC_API_KEY` | `sk-ant-test...` | Secret API key for Claude 3.5 Sonnet |
| `OPENAI_API_KEY` | `sk-test...` | Fallback API key for GPT-4o |
| `LANGFUSE_PUBLIC_KEY` | `pk-lf-...` | Langfuse tracing telemetry public key |
| `LANGFUSE_SECRET_KEY` | `sk-lf-...` | Langfuse tracing telemetry secret key |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Langfuse observability endpoint |

---

## 3. Observability & Diagnostic Metrics

IronGraph-Engine exposes standard Prometheus metrics at `/metrics`:

- `irongraph_adaptation_duration_seconds{quantile="0.95"}`: p95 latency from request submission to final complete SSE event.
- `irongraph_sfr_optimizations_total{strategy="aps_compression"}`: Counter tracking applied time-density or joint-sparing optimizations.
- `irongraph_biomechanical_pruning_count`: Number of contraindicated exercises pruned prior to LLM prompting.
- `irongraph_effective_volume_deficit_rejections`: Counter tracking reflection cycles triggered by volume loss.
- `irongraph_ttft_seconds`: Time to first streaming token.

### Health Probes
- **Liveness (`GET /health/live`)**: Returns `200 {"status": "alive"}` if FastAPI process is responsive.
- **Readiness (`GET /health/ready`)**: Performs active ping checks to PostgreSQL (`SELECT 1`), Redis (`PING`), and Qdrant cluster health. Returns `503 Service Unavailable` if any dependency is down.

---

## 4. Disaster Recovery & Incident Runbooks

### Runbook A: Stale Lifter Session Lock in Redis
*Symptom*: Client receives `409 Conflict: Lifter session locked by another active adaptation` indefinitely after an aborted connection.
*Resolution*:
```bash
# Query active session lock key
docker compose exec redis redis-cli KEYS "lock:lifter:*"
# Delete specific stuck lifter lock (TTL is normally 30s)
docker compose exec redis redis-cli DEL "lock:lifter:<LIFTER_ID>"
```

### Runbook B: Rebuilding In-Memory Biomechanical Graph
*Symptom*: In-memory NetworkX exercise graph in Redis is suspected of desynchronization after a database migration.
*Resolution*:
```bash
# Triggers cache re-population from PostgreSQL graph tables
curl -X POST "$IRONGRAPH_URL/v1/system/rebuild-graph" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```
