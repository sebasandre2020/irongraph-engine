"""Integration tests for Biomechanical Exercise Substitution API."""


def test_substitute_exercise_success(client):
    payload = {
        "exercise_id": "barbell_back_squat",
        "available_equipment": ["hack_squat_machine", "leg_press_machine"],
        "max_axial_stress": 4
    }
    response = client.post("/v1/exercises/substitute", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["original_exercise_id"] == "barbell_back_squat"
    substitutes = data["substitutes"]
    assert len(substitutes) >= 1

    sub_ids = [s["exercise_id"] for s in substitutes]
    assert "hack_squat" in sub_ids or "leg_press" in sub_ids
    for s in substitutes:
        assert s["axial_stress_rating"] <= 4


def test_substitute_nonexistent_exercise(client):
    payload = {
        "exercise_id": "nonexistent_movement_xyz",
        "available_equipment": ["dumbbells"]
    }
    response = client.post("/v1/exercises/substitute", json=payload)
    assert response.status_code == 404
