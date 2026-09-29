"""Integration tests for Workout Autoregulation & SSE Streaming."""

from app.schemas.adaptation import (
    DailyDrawbacks,
    PlannedExercise,
    PlannedWorkout,
)


def test_adapt_workout_json_response(client, test_lifter_id):
    """Test full workout adaptation returning JSON payload."""
    payload = {
        "drawbacks": {
            "sleep_hours": 4.5,
            "available_minutes": 30,
            "occupied_equipment": ["squat_rack"],
            "localized_pain_symptoms": ["lower_back_tightness"],
            "subjective_readiness_1_to_10": 4
        },
        "planned_workout": {
            "title": "Leg & Pull Hypertrophy",
            "target_duration_min": 60,
            "exercises": [
                {
                    "exercise_id": "barbell_back_squat",
                    "sets": 3,
                    "target_reps": "6-8",
                    "target_rir": 2.0,
                    "prescribed_load_kg": 140.0
                },
                {
                    "exercise_id": "incline_dumbbell_press",
                    "sets": 3,
                    "target_reps": "8-10",
                    "target_rir": 2.0,
                    "prescribed_load_kg": 40.0
                },
                {
                    "exercise_id": "barbell_bent_over_row",
                    "sets": 3,
                    "target_reps": "8-10",
                    "target_rir": 2.0,
                    "prescribed_load_kg": 90.0
                }
            ]
        },
        "hypertrophy_preferences": {
            "enable_antagonist_paired_sets": True,
            "enable_rest_pause_myo_reps": True,
            "target_rir_buffer": 1.5,
            "preserve_effective_volume": True
        }
    }

    response = client.post(f"/v1/lifters/{test_lifter_id}/adapt", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "COMMITTED"
    assert "adapted_workout" in data
    workout = data["adapted_workout"]

    # Session compressed within available minutes (<= 30 min)
    assert workout["estimated_duration_min"] <= 30

    # Back squat substituted by leg press or hack squat due to sleep + squat rack occupied + lower back tightness
    exercise_ids = [ex["exercise_id"] for ex in workout["exercises"]]
    assert "barbell_back_squat" not in exercise_ids
    assert "hack_squat" in exercise_ids or "leg_press" in exercise_ids

    # Barbell bent over row substituted by chest-supported tbar row
    assert "barbell_bent_over_row" not in exercise_ids
    assert "chest_supported_tbar_row" in exercise_ids

    # Loads autoregulated down due to 4.5h sleep (scale factor < 1.0)
    for ex in workout["exercises"]:
        if ex["exercise_id"] == "hack_squat":
            assert ex["recommended_load_kg"] < 140.0

    # Coaching prose generated
    assert len(data["coaching_prose"]) > 20


def test_adapt_workout_sse_streaming(client, test_lifter_id):
    """Test workout adaptation streaming Server-Sent Events."""
    payload = {
        "drawbacks": {
            "sleep_hours": 5.0,
            "available_minutes": 35,
            "occupied_equipment": [],
            "localized_pain_symptoms": [],
            "subjective_readiness_1_to_10": 6
        }
    }
    headers = {"Accept": "text/event-stream"}
    response = client.post(f"/v1/lifters/{test_lifter_id}/adapt", json=payload, headers=headers)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    content = response.text
    assert "event: token" in content
    assert "event: workout_delta" in content
    assert "event: complete" in content
