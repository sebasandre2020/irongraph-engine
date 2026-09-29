# Implementation Roadmap: IronGraph-Engine

## Current Status: Phase 2 Completed (Architecture & Scaffolding)
All architectural models, OpenAPI 3.1 contracts, JSON schemas, PostgreSQL DDL schemas, Docker Compose configurations, and CI validation workflows are established and verified.

---

## Phase 3: Core Implementation Milestones

### Milestone 1: FastAPI Control Plane & Lifter Schemas (Target: Week 1)
- [ ] Implement `app/main.py` with FastAPI lifespan handler and CORS middleware.
- [ ] Implement Pydantic v2 models (`CreateLifterRequest`, `AdaptationRequest`, `AdaptedWorkout`).
- [ ] Setup JWT authentication dependency with scope extraction.
- [ ] Implement Redis connection pool and distributed locking manager (`lock:lifter:{id}`).

### Milestone 2: Biomechanical Graph & Rule Engine (Target: Week 2)
- [ ] Implement `GraphRepository` using `asyncpg` with connection pooling.
- [ ] Build in-memory `NetworkX` graph wrapper for exercise taxonomy and joint stress ratings.
- [ ] Implement deterministic `BiomechanicalRuleEngine` specifications:
  - `SpinalCompressiveThresholdRule`
  - `ContraindicationPruningRule`
  - `EquipmentAvailabilityRule`
- [ ] Unit tests for rule engine verifying 100% rejection of contraindicated exercises.

### Milestone 3: Hypertrophy Math Engine (Target: Week 3)
- [ ] Implement `HypertrophyMathEngine` with algorithms for:
  - Stimulus-to-Fatigue Ratio (SFR) calculation
  - Effective volume preservation accounting
  - Antagonist Paired Sets (APS) pairing and rest staggering
  - Myo-reps and rest-pause density formulas
  - Dynamic RIR load scaling based on sleep hours

### Milestone 4: LangGraph Hypertrophy Agent & SSE Streaming (Target: Week 4)
- [ ] Construct `StateGraph(AutoregulationState)` with reflection cycles.
- [ ] Implement `LLMProviderStrategy` with Anthropic Claude 3.5 Sonnet and OpenAI GPT-4o adapters.
- [ ] Implement real-time SSE streamer (`sse-starlette`) yielding chunked coaching rationale and structured workout deltas.
- [ ] Verify that effective volume loss triggers reflection critique and set density compression.

### Milestone 5: Qdrant Sports Science Lore Retrieval (Target: Week 5)
- [ ] Setup Qdrant collection initialization for peer-reviewed literature embeddings.
- [ ] Implement context compiler injecting density study citations into agent prompts.
- [ ] Implement Langfuse tracing middleware recording latency and token costs.

### Milestone 6: Model Context Protocol (MCP) Adapter (Target: Week 6)
- [ ] Implement MCP server layer exposing `adapt_workout`, `substitute_exercise`, and `get_lifter_profile` tools.
- [ ] Test integration with Claude Desktop.

### Milestone 7: Cloud Deployment & CI/CD Activation (Target: Week 7)
- [ ] Provision AWS staging environment using Terraform (`infra/terraform`).
- [ ] Activate GitHub Actions deployment workflow with Trivy vulnerability scanning.
- [ ] Execute automated load test verifying p95 adaptation latency under concurrent load.
