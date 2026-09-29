# Lifters API Specification: IronGraph-Engine

## 1. Register Lifter Profile
Initializes a new lifter profile establishing baseline 1RMs, experience tier, active injury contraindications, and personalized muscle group volume landmarks (Minimum Effective Volume - MEV, Maximum Adaptive Volume - MAV, Maximum Recoverable Volume - MRV).

- **Method & Path**: `POST /v1/lifters`
- **Scope**: `lifters:write`
- **Latency SLA**: p95 < 40ms

### Request Payload Example
```json
{
  "name": "Alex Turner",
  "experience_tier": "advanced",
  "volume_landmarks_mev_mrv": {
    "quads": { "mev": 8, "mav": 14, "mrv": 18 },
    "hamstrings": { "mev": 6, "mav": 10, "mrv": 14 },
    "chest": { "mev": 8, "mav": 14, "mrv": 20 },
    "back": { "mev": 10, "mav": 16, "mrv": 22 }
  },
  "baseline_1rms": {
    "barbell_back_squat": 160.0,
    "incline_dumbbell_press": 42.5,
    "barbell_bent_over_row": 110.0
  },
  "active_contraindications": [
    "acute_lumbar_strain"
  ]
}
```

### Response Payload (`201 Created`)
```json
{
  "lifter_id": "f1e2d3c4-b5a6-7890-1234-567890abcdef",
  "name": "Alex Turner",
  "experience_tier": "advanced",
  "volume_landmarks_mev_mrv": {
    "quads": { "mev": 8, "mav": 14, "mrv": 18 },
    "hamstrings": { "mev": 6, "mav": 10, "mrv": 14 },
    "chest": { "mev": 8, "mav": 14, "mrv": 20 },
    "back": { "mev": 10, "mav": 16, "mrv": 22 }
  },
  "created_at": "2026-09-27T18:00:00.000Z"
}
```

---

## 2. Get Lifter Profile
Retrieves lifter profile, active contraindications, and accumulated weekly fatigue metrics.

- **Method & Path**: `GET /v1/lifters/{lifter_id}`
- **Scope**: `lifters:read`
- **Latency SLA**: p95 < 20ms
