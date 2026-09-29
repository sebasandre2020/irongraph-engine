"""Unit tests for Biomechanical Graph & Rule Engine."""

import pytest
from app.engine.biomechanical_graph import default_graph
from app.engine.rule_engine import BiomechanicalRuleEngine
from app.schemas.adaptation import DailyDrawbacks


@pytest.fixture
def rule_engine():
    return BiomechanicalRuleEngine(default_graph)


def test_spinal_compressive_threshold_rule_triggers_on_low_sleep(rule_engine):
    """Under 5 hours of sleep, axial stress >= 7 must be pruned."""
    squat = default_graph.get_exercise("barbell_back_squat")  # axial rating 9
    drawbacks = DailyDrawbacks(sleep_hours=4.0, available_minutes=45)

    is_safe, reason = rule_engine.evaluate_axial_safety(squat, drawbacks)
    assert not is_safe
    assert "High axial stress" in reason
    assert "sleep deprivation" in reason


def test_spinal_compressive_threshold_rule_permits_when_rested(rule_engine):
    """When well rested (>= 7 hours), axial stress 9 is permitted."""
    squat = default_graph.get_exercise("barbell_back_squat")
    drawbacks = DailyDrawbacks(sleep_hours=8.0, available_minutes=60, subjective_readiness_1_to_10=8)

    is_safe, _ = rule_engine.evaluate_axial_safety(squat, drawbacks)
    assert is_safe


def test_contraindication_pruning_rule_rejects_lumbar_strain(rule_engine):
    """Acute lumbar strain must prune Romanian deadlifts and barbell rows."""
    deadlift = default_graph.get_exercise("romanian_deadlift")
    drawbacks = DailyDrawbacks(sleep_hours=7.0, available_minutes=60)
    contraindications = ["acute_lumbar_strain"]

    is_safe, reason = rule_engine.evaluate_contraindications(deadlift, drawbacks, contraindications)
    assert not is_safe
    assert "lumbar strain" in reason


def test_equipment_availability_rule(rule_engine):
    """Occupied equipment blocks dependent exercises."""
    squat = default_graph.get_exercise("barbell_back_squat")
    drawbacks = DailyDrawbacks(
        sleep_hours=7.5,
        available_minutes=60,
        occupied_equipment=["squat_rack"]
    )

    is_safe, reason = rule_engine.evaluate_equipment(squat, drawbacks)
    assert not is_safe
    assert "squat_rack" in reason


def test_deterministic_pruning_and_substitution(rule_engine):
    """Barbell Back Squat -> Machine Hack Squat or Leg Press when lumbar safety or equipment is violated."""
    drawbacks = DailyDrawbacks(
        sleep_hours=4.5,
        available_minutes=30,
        occupied_equipment=["squat_rack"],
        localized_pain_symptoms=["lower_back_tightness"]
    )
    available_equipment = ["hack_squat_machine", "dumbbells", "tbar_machine"]

    substitute_node, note = rule_engine.prune_and_substitute(
        exercise_id="barbell_back_squat",
        drawbacks=drawbacks,
        active_contraindications=["acute_lumbar_strain"],
        available_equipment=available_equipment
    )

    assert substitute_node.id == "hack_squat"
    assert substitute_node.axial_stress_rating <= 4
    assert "Substituted 'Barbell Back Squat' -> 'Machine Hack Squat'" in note
