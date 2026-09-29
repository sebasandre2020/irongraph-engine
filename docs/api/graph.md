# Biomechanical Graph API Specification: IronGraph-Engine

## 1. 1:1 Biomechanical Exercise Substitution
Finds the top biomechanically matched exercise substitutes for a target exercise. The algorithm filters out occupied equipment, honors active injury contraindications, and matches target muscle length-tension curves and resistance profiles.

- **Method & Path**: `POST /v1/exercises/substitute`
- **Scope**: `exercises:read`
- **Latency SLA**: p95 < 25ms

### Request Payload Example
```json
{
  "target_exercise_id": "barbell_back_squat",
  "reason_for_substitution": "occupied_equipment_and_lumbar_fatigue",
  "available_equipment": ["hack_squat_machine", "leg_press_machine"],
  "max_axial_stress": 4,
  "top_k": 2
}
```

### Response Payload (`200 OK`)
```json
{
  "target_exercise_id": "barbell_back_squat",
  "substitutes": [
    {
      "exercise_id": "hack_squat",
      "name": "Machine Hack Squat",
      "axial_stress": 3,
      "sfr_rating": "very_high",
      "compatibility_score": 0.96,
      "biomechanical_rationale": "Matches quad knee flexion vector with fixed pelvic support; eliminates axial spinal shear."
    },
    {
      "exercise_id": "leg_press",
      "name": "45-Degree Leg Press",
      "axial_stress": 2,
      "sfr_rating": "high",
      "compatibility_score": 0.91,
      "biomechanical_rationale": "High quad mechanical tension with zero spinal compression."
    }
  ]
}
```
