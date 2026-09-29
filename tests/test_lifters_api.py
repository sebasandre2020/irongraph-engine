"""Integration tests for Lifters API."""

from uuid import uuid4


def test_create_lifter_profile(client):
    payload = {
        "name": "Jordan Hayes",
        "experience_tier": "intermediate",
        "volume_landmarks": {
            "chest": {"mev": 8, "mav": 14, "mrv": 20},
            "back": {"mev": 10, "mav": 16, "mrv": 22},
            "quads": {"mev": 8, "mav": 12, "mrv": 18},
            "hamstrings": {"mev": 6, "mav": 10, "mrv": 14}
        },
        "baseline_1rms": {
            "barbell_back_squat": 140.0,
            "incline_dumbbell_press": 36.0
        },
        "active_contraindications": []
    }
    response = client.post("/v1/lifters", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jordan Hayes"
    assert "id" in data
    assert data["baseline_1rms"]["barbell_back_squat"] == 140.0


def test_get_lifter_profile(client, test_lifter_id):
    response = client.get(f"/v1/lifters/{test_lifter_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alex Turner"
    assert "acute_lumbar_strain" in data["active_contraindications"]


def test_get_nonexistent_lifter(client):
    random_id = uuid4()
    response = client.get(f"/v1/lifters/{random_id}")
    assert response.status_code == 404
