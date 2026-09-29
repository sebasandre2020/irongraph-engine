# Workouts API Specification: IronGraph-Engine

## 1. Overview
The Workouts subsystem manages planned training session templates prior to atypical day-to-day adaptations.

## 2. Planned Workout Schema Structure
A planned workout includes targeted muscle groups, planned sets, rep targets, baseline target RIR, and rest intervals.

```json
{
  "title": "Lower Body & Upper Pull Hypertrophy A",
  "target_duration_min": 70,
  "target_muscle_groups": ["quads", "hamstrings", "lats"],
  "exercises": [
    {
      "exercise_id": "barbell_back_squat",
      "planned_sets": 4,
      "planned_reps": "6-8",
      "target_rir": 2,
      "planned_load_kg": 125.0,
      "rest_seconds": 180
    }
  ]
}
```
When an atypical day occurs, this template serves as the baseline input to the adaptation endpoint.
