# Documentation Index: IronGraph-Engine

**Status**: Technical blueprint index and navigation schema.

---

## 1. Core Documentation Map

| Area | Documentation Entry Point | Description |
| :--- | :--- | :--- |
| **Recruiter Introduction & Pitch** | [README.md](README.md) | Fast 30-second read, architecture overview, sample curl requests |
| **System Architecture** | [Architecture.md](Architecture.md) | Topology diagrams, request lifecycles, hypertrophy math, SFR models |
| **Classes & State Machines** | [Class.md](Class.md) | Component responsibilities, LangGraph state transitions, design patterns |
| **Operational Runbook** | [Operations.md](Operations.md) | Local runbook, docker-compose commands, telemetry, disaster recovery |
| **Project Brief & Vision** | [PROJECT_BRIEF.md](PROJECT_BRIEF.md) | Problem statement, user personas, hypertrophy principles, non-goals |
| **Phase 3 Roadmap** | [docs/roadmap.md](docs/roadmap.md) | Implementation milestones, acceptance criteria, and rollout phases |
| **Scaffold Verification** | [docs/validation.md](docs/validation.md) | Empirical test records and scaffold integrity checks |
| **Academic & Industry References** | [docs/references.md](docs/references.md) | Peer-reviewed exercise physiology and systems engineering literature |

---

## 2. API Contract & Endpoint Map

| Method & Path | Authorization Scope | Contract Specification | Description |
| :--- | :--- | :--- | :--- |
| `POST /v1/lifters` | `lifters:write` | [Lifters API](docs/api/lifters.md) | Register lifter profile and volume landmarks |
| `GET /v1/lifters/{lifter_id}` | `lifters:read` | [Lifters API](docs/api/lifters.md) | Retrieve lifter profile, 1RMs, and fatigue history |
| `POST /v1/lifters/{id}/adapt` | `adaptations:write`| [Adaptations API](docs/api/adaptations.md) | Adapt planned session to atypical friction with SSE stream |
| `POST /v1/exercises/substitute`| `exercises:read` | [Graph API](docs/api/graph.md) | 1:1 Biomechanical exercise substitute matching |
| `GET /v1/exercises/{id}/graph` | `exercises:read` | [Graph API](docs/api/graph.md) | Inspect anatomical links and joint stress ratings |
| `GET /health/live` | Public Probe | [Conventions](docs/api/conventions.md) | Liveness probe for ALB and container monitors |
| `GET /health/ready` | Public Probe | [Conventions](docs/api/conventions.md) | Readiness probe verifying DB, Redis, and Qdrant links |

*Detailed Schema Files:* [OpenAPI 3.1 Contract](contracts/openapi.json) · [JSON Schemas](contracts/schemas.json) · [API Conventions](docs/api/conventions.md)

---

## 3. Subsystem & Service Specifications

| Subsystem | Core Responsibilities | Architectural Specification |
| :--- | :--- | :--- |
| **API Admission & Control Plane** | Auth verification, Pydantic validation, Redis locks | [Control Plane](docs/services/control-plane.md) |
| **Specialized Hypertrophy Agent** | Evidence-based hypertrophy logic, volume preservation | [Hypertrophy Agent](docs/services/hypertrophy-agent.md) |
| **Biomechanical Graph Engine** | Anatomical property graph, joint contraindications | [Graph Engine](docs/services/graph-engine.md) |
| **Autoregulation Math Engine** | SFR optimization, Antagonist Paired Sets, Myo-reps | [Autoregulation](docs/services/autoregulation.md) |
| **Sports Science Lore Retrieval** | Peer-reviewed study embeddings, Qdrant collection | [Lore Retrieval](docs/services/retrieval.md) |
| **Telemetry & Observability** | Langfuse LLM traces, Prometheus metrics, logging | [Observability](docs/services/observability.md) |
| **Cloud Infrastructure (AWS)** | ECS Fargate, RDS PostgreSQL, ElastiCache, S3 | [Deployment Blueprint](docs/delivery/deployment.md) |
| **Continuous Integration & Delivery**| GitHub Actions CI/CD pipeline, container builds | [CI/CD Blueprint](docs/delivery/ci-cd.md) |

---

## 4. Scaffolding Artifacts & Configuration

- **Docker Environment**: [compose.yaml](compose.yaml) · [infra/docker/Dockerfile.blueprint](infra/docker/Dockerfile.blueprint)
- **Database Schema**: [infra/postgres/001_init_schema.sql](infra/postgres/001_init_schema.sql)
- **Terraform IaC**: [infra/terraform/main.tf](infra/terraform/main.tf) · [infra/terraform/variables.tf](infra/terraform/variables.tf) · [infra/terraform/outputs.tf](infra/terraform/outputs.tf)
- **Validation & Scripts**: [scripts/validate_scaffold.py](scripts/validate_scaffold.py) · [requirements-dev.txt](requirements-dev.txt)
- **Sample Payloads**: [examples/create_lifter_profile.json](examples/create_lifter_profile.json) · [examples/planned_workout.json](examples/planned_workout.json) · [examples/atypical_adaptation_request.json](examples/atypical_adaptation_request.json) · [examples/adapted_workout_response.json](examples/adapted_workout_response.json) · [examples/exercise_substitution.json](examples/exercise_substitution.json)
