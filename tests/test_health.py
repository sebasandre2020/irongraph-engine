"""Test health probes."""


def test_liveness_probe(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data


def test_readiness_probe(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "postgres" in data["dependencies"]
    assert "redis" in data["dependencies"]
