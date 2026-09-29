# Project Brief: IronGraph-Engine

## Executive Summary
**IronGraph-Engine** is a production-grade, consumable AI engine and headless backend service architected to solve a universal struggle in resistance training: **adapting workout sessions to real-world, atypical day-to-day drawbacks (severe sleep deprivation, acute time crunches, crowded gym equipment, joint inflammation) without losing ground on progressive overload and while maximizing skeletal muscle hypertrophy.**

Standard fitness applications and static spreadsheets fail because they treat workout programs as rigid dogma: if a lifter only has 30 minutes instead of 75, or only slept 4 hours, their only options are skipping the workout, cutting corners randomly, or risking injury and overtraining on heavy axial compound lifts. Generic AI chatbots fail equally hard by hallucinating meaningless "light recovery circuits" that discard mechanical tension—the primary stimulus for muscle growth.

IronGraph-Engine introduces a **Specialized Hypertrophy & Sports Performance Agent** integrated with a **Biomechanical Property Graph** and an **Evidence-Based Autoregulation State Machine**. When atypical constraints strike, the engine does not abandon the plan; it mathematically recalibrates sets, reps, load intensity (RPE / RIR), rest intervals, and exercise modalities to preserve target effective volume and maximize the Stimulus-to-Fatigue Ratio (SFR).

---

## Target Personas & Core Problems

1. **Serious Lifters & Bodybuilders Facing Life Friction**: Lifters committed to progressive overload who encounter unavoidable life events—work deadlines leaving 30 minutes to train, newborn sleep disruption, or crowded gym peak hours—and need deterministic, science-backed workout adaptations that keep them growing.
2. **Strength & Conditioning Coaches / PT Platforms**: Platforms seeking an intelligent, headless API that handles real-time workout autoregulation and exercise substitution without human coach bottlenecks.
3. **Endurance & Hybrid Athletes**: Athletes managing high systemic fatigue from concurrent training who require intelligent volume reduction and joint-friendly mechanical tension targeting.

---

## Specialized Hypertrophy Agent & Scientific Principles

The engine's core intelligence is driven by a specialized **Hypertrophy & Sports Performance Agent** grounded in contemporary exercise physiology literature (Schoenfeld, Israetel, Beardsley, Helms):

1. **Mechanical Tension as the Primary Growth Driver**: High-threshold motor unit recruitment achieved by taking sets within 0–3 Reps in Reserve (RIR) under controlled eccentric and concentric phases.
2. **Effective Volume vs. Junk Volume**: Progress is dictated by hard, high-effort sets (effective reps). More sets beyond a lifter's recovery capacity (MRV) provide diminishing returns and elevated fatigue.
3. **Stimulus-to-Fatigue Ratio (SFR) Optimization**:
   $$\text{SFR} = \frac{\text{Local Muscle Mechanical Tension}}{\text{Axial Stress} + \text{Joint Inflammation} + \text{CNS Fatigue}}$$
   On sleep-deprived or low-recovery days, high-axial exercises (e.g. Barbell Squats, Romanian Deadlifts) are dynamically swapped for high-SFR, highly stabilized movements (e.g. Hack Squats, Belt Squats, Chest-Supported T-Bar Rows) matching or exceeding muscle recruitment with half the systemic strain.
4. **Time-Density Intensifiers for Acute Time Crunches**:
   - **Antagonist Paired Sets (APS)**: Interleaving non-competing exercises (e.g., Incline Dumbbell Press + Chest-Supported Row) cutting workout duration by up to 45% without reducing volume or loads.
   - **Rest-Pause / Myo-Reps**: Utilizing 1 activation set followed by short 15-second rests and 3–4 mini-sets of 3–5 reps, achieving equivalent effective high-tension reps in 4 minutes as 3 traditional sets in 10 minutes.
   - **Lengthened Partials**: Emphasizing peak mechanical tension in the stretched muscle position for maximum muscle hypertrophy efficiency.

---

## Architectural Pillars & Design Principles

- **Consumable Service Over Monolithic App**: Exposes pure OpenAPI 3.1 REST endpoints, Server-Sent Events (SSE) token and workout adaptation streams, and Model Context Protocol (MCP) tools for external AI clients (Claude Desktop, mobile apps).
- **Anatomical & Equipment Property Graph**: Exercises, movement patterns, muscle heads, joints, equipment requirements, and biomechanical contraindications are modeled as an explicit graph ($G = (V, E)$) in PostgreSQL and Redis.
- **Deterministic Autoregulation Guardrails**: Before LLM prompting, deterministic rules calculate volume thresholds and filter biomechanically contraindicated movements.
- **LangGraph Autoregulation State Machine**: Coordinates intake of daily drawbacks, graph context extraction, volume/load adaptation, reflection cycles, and client streaming.
- **Production Observability**: Full tracing of prompt tokens, latency, and hypertrophy reasoning via Langfuse and Prometheus.

---

## Target Technology Stack
- **Language & Runtime**: Python 3.12, FastAPI, AsyncIO, Pydantic v2
- **Data Persistence**: PostgreSQL 16 (Relational tables, JSONB workout logs, recursive graph CTEs), Redis 7 (Active session cache, distributed locks, rate limiting)
- **Vector Retrieval**: Qdrant (Biomechanics and exercise physiology literature embeddings)
- **Agent Orchestration**: LangGraph (Cyclic state machine with reflection and constraint checking)
- **Protocols**: OpenAPI 3.1, Server-Sent Events (SSE), Model Context Protocol (MCP) JSON-RPC 2.0
- **Infrastructure & Delivery**: Docker, Docker Compose, AWS ECS Fargate, AWS RDS PostgreSQL, AWS S3, Terraform, GitHub Actions

---

## Scope & Non-Goals
### In Scope
- Lifter profile initialization (training experience, volume landmarks MEV/MRV, baseline 1RMs/RIR).
- Ingestion of planned workouts and daily atypical drawbacks (sleep hours, available minutes, equipment blockers, joint discomfort).
- Algorithmic adaptation of sets, reps, loads (% 1RM or RPE), rest intervals, and exercise modalities.
- Application of evidence-based time-savers (Antagonist Paired Sets, Myo-reps, Drop sets).
- Dual-channel SSE streaming (coaching narrative cues + structured JSON workout schemas).
- 1:1 Biomechanical exercise substitution engine with resistance curve matching.

### Out of Scope (Non-Goals)
- Video computer-vision form tracking via mobile cameras (focus is on program architecture and autoregulation).
- Calorie/macro meal scanning (handled by specialized nutrition microservices like MacroSync-MCP).
- Medical diagnosis or physical therapy treatment plans (strictly performance and hypertrophy optimization).
