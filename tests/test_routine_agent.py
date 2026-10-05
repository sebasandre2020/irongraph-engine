"""Tests for Text-Based Routine Adaptation Agent and Frontend."""

import os
import pytest
from app.engine.routine_parser import extract_day_sections, parse_exercise_line


def test_routine_parser_on_gymrutine_file():
    """Verify parser correctly extracts distinct training days from GymRutine.txt."""
    assert os.path.exists("GymRutine.txt")
    with open("GymRutine.txt", "r", encoding="utf-8") as f:
        content = f.read()

    days = extract_day_sections(content)
    assert len(days) >= 4

    day_titles = [d.title for d in days]
    assert any("PULL A" in t for t in day_titles)
    assert any("PUSH A" in t for t in day_titles)
    assert any("LEGS A" in t for t in day_titles)

    # First day has exercises parsed
    first_day = days[0]
    assert len(first_day.exercises) >= 4
    ex_names = [e.name for e in first_day.exercises]
    assert "Lat Pulldown (Cable)" in ex_names
    assert "Seated Cable Row" in ex_names


def test_get_example_routine_endpoint(client):
    """GET /v1/agent/example-routine returns GymRutine.txt data and day sections."""
    response = client.get("/v1/agent/example-routine")
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "GymRutine.txt"
    assert len(data["available_days"]) >= 4
    assert "full_text" in data


def test_adapt_text_routine_with_drawbacks(client):
    """POST /v1/agent/adapt-routine handles sleep deficit, time crunch, and equipment blocker."""
    raw_snippet = """
    DÍA 1: PULL A (Amplitud/Pico)
    Jalón al pecho (Polea): 4 series x 12 reps. 120kg.
    Remo sentado (agarre estrecho): 3 series x 12 reps. 59kg.
    Mid row maquina (espalda media): 3 series x 10 reps.
    Curl predicador (barra z): 2 series x 12 reps. 15 kg.
    """

    payload = {
        "routine_text": raw_snippet,
        "sleep_hours": 5.0,
        "baseline_sleep_hours": 8.0,
        "available_minutes": 25,
        "occupied_equipment": ["cable_pulldown"],
        "localized_pain_symptoms": ["lower_back_tightness"],
        "subjective_readiness_1_to_10": 4,
        "preferred_language": "es"
    }

    response = client.post("/v1/agent/adapt-routine", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["estimated_duration_min"] <= 30
    assert data["effective_volume_percentage"] == 100.0
    assert len(data["comparisons"]) >= 3

    # Check that cable pulldown was substituted due to occupied equipment
    pulldown_comp = next((c for c in data["comparisons"] if "Lat Pulldown" in c["original_name"] or "Jalón" in c["original_name"]), None)
    if pulldown_comp:
        assert pulldown_comp["status_tag"] in ["SUBSTITUTED", "APS_PAIRED", "LOAD_AUTOREGULATED"]

    # Check coaching rationale is populated
    assert len(data["coaching_rationale"]) > 20

    # Check new fields: load_delta_percent & equipment_category
    assert pulldown_comp["equipment_category"] is not None
    assert pulldown_comp["load_delta_percent"] is not None
    assert pulldown_comp["load_delta_percent"] < 0  # Reduced due to 5.0h sleep


def test_smart_plate_rounding_and_station_pairing(client):
    """Verify smart gym load increments and same_station_only constraint."""
    from app.ai.agent_service import round_gym_weight

    # Test barbell rounding
    assert round_gym_weight(123.4, unit="kg", equipment="barbell") in [120, 122.5, 125]
    # Test dumbbell rounding
    assert round_gym_weight(21.3, unit="kg", equipment="dumbbell") in [20, 22]
    # Test lbs rounding
    assert round_gym_weight(136.2, unit="lbs") in [135, 140]

    raw_snippet = """
    DIA 1: TEST PAIR
    Press de banca: 3 series x 10 reps. 80kg.
    Remo con mancuernas: 3 series x 10 reps. 24kg.
    """
    payload = {
        "routine_text": raw_snippet,
        "available_minutes": 25,
        "same_station_only": True
    }
    response = client.post("/v1/agent/adapt-routine", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["comparisons"]) == 2


def test_frontend_home_route(client):
    """GET / serves the interactive responsive HTML UI with Gym Mode."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "IronGraph Engine" in response.text
    assert "Inconvenientes del Día" in response.text
    assert "Cronómetro de Descanso" in response.text
    assert "Modo Gimnasio" in response.text
    assert "Seleccionar Día de Rutina" in response.text
