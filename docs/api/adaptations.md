# Adaptations API Specification: IronGraph-Engine

## 1. Adapt Workout to Atypical Friction
Accepts planned workout parameters alongside real-world day-to-day drawbacks (sleep deprivation, acute time crunches, occupied gym machines, joint tightness). Employs the **Hypertrophy & Sports Performance Agent** to adapt sets, reps, loads, rest intervals, and exercise modalities, streaming coaching rationale and structured workout schemas over Server-Sent Events (SSE).

- **Method & Path**: `POST /v1/lifters/{lifter_id}/adapt`
- **Scope**: `adaptations:write`
- **Latency SLAs**:
  - Biomechanical Pruning: < 15ms
  - Time to First Token (TTFT): < 750ms
  - Total Adaptation Completion (p95): < 3000ms

### Request Headers
```http
Authorization: Bearer <TOKEN>
Content-Type: application/json
Accept: text/event-stream
```

### Request Payload Example
```json
{
  "planned_workout_id": "e4d3c2b1-a098-7654-3210-fedcba987654",
  "drawbacks": {
    "sleep_hours": 4.5,
    "available_minutes": 30,
    "occupied_equipment": ["squat_rack"],
    "localized_pain_symptoms": ["lower_back_tightness"],
    "subjective_readiness_1_to_10": 4
  },
  "hypertrophy_preferences": {
    "enable_antagonist_paired_sets": true,
    "enable_rest_pause_myo_reps": true,
    "target_rir_buffer": 1.5,
    "preserve_effective_volume": true
  }
}
```

---

## 2. Server-Sent Events (SSE) Execution Trace

When `Accept: text/event-stream` is requested, the endpoint returns HTTP 200 with `Transfer-Encoding: chunked` and emits structured event frames:

```text
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

event: token
data: {"text": "Detected 4.5h sleep and acute lumbar tightness."}

event: token
data: {"text": " Eliminating high-axial spinal compression. Barbell Squats are converted to Hack Squats (low foot placement for maximal quad mechanical tension)."}

event: token
data: {"text": " Incline DB Press and Chest-Supported Rows are paired in an Antagonist Paired Set to compress session time to 28 minutes while securing 9 effective hypertrophy sets."}

event: workout_delta
data: {
  "title": "Adapted Hypertrophy: High-SFR Quad & Pull Blast (30-min Express)",
  "estimated_duration_min": 28,
  "total_effective_sets": 9,
  "sfr_rating": "VERY_HIGH",
  "exercises": [
    {
      "exercise_id": "hack_squat",
      "exercise_label": "Machine Hack Squat",
      "sets": 3,
      "rep_range": "8-10",
      "target_rir": 1.5,
      "recommended_load_kg": 110.0,
      "rest_seconds": 90,
      "intensifier_type": "lengthened_partials_last_set"
    }
  ]
}

event: complete
data: {"adaptation_id": "adapt_01HXZ7K8M9NPQR0123456789AB", "status": "COMMITTED"}
```

---

## 3. Failure & Error Modes

### 1. Concurrent Session Conflict (`409 Conflict`)
Occurs when another adaptation is currently generating for the same lifter:
```json
{
  "type": "https://irongraph.internal/errors/session-locked",
  "title": "Lifter Session Locked",
  "status": 409,
  "detail": "Lifter 'f1e2d3c4-b5a6-7890-1234-567890abcdef' has an active executing adaptation. Please retry."
}
```
