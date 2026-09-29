"""Unit tests for Hypertrophy Science & Sports Performance Mathematics."""

from app.engine.hypertrophy_math import HypertrophyMathEngine


def test_load_scaling_factor_normal_sleep():
    """8.0 hours of sleep should have no load deduction (alpha = 1.0)."""
    alpha = HypertrophyMathEngine.calculate_load_scaling_factor(sleep_hours=8.0, subjective_readiness=8)
    assert alpha == 1.0


def test_load_scaling_factor_severe_sleep_deprivation():
    """4.5 hours of sleep scales load down by approximately 6-8%."""
    # alpha = 1.0 - (7.0 - 4.5)/20.0 = 1.0 - 0.125 = 0.875
    alpha = HypertrophyMathEngine.calculate_load_scaling_factor(sleep_hours=4.5, subjective_readiness=5)
    assert 0.85 <= alpha <= 0.90


def test_autoregulate_weight():
    """100kg baseline scaled for 4.5h sleep becomes ~87.5kg."""
    scaled = HypertrophyMathEngine.autoregulate_weight(
        baseline_weight=100.0,
        sleep_hours=4.5,
        subjective_readiness=5
    )
    assert scaled == 87.5


def test_calculate_sfr():
    """Stimulus-to-fatigue ratio reflects ratio of mechanical tension to fatigue factors."""
    # Machine Hack Squat: Tension 9, Axial 2, Joint 1, CNS 2 -> 9 / 5 = 1.8
    sfr_hack = HypertrophyMathEngine.calculate_sfr(
        mechanical_tension=9.0,
        axial_stress=2.0,
        joint_inflammation=1.0,
        cns_fatigue=2.0
    )
    assert sfr_hack == 1.80

    # Barbell Back Squat on bad recovery: Tension 9, Axial 9, Joint 3, CNS 7 -> 9 / 19 = 0.47
    sfr_squat = HypertrophyMathEngine.calculate_sfr(
        mechanical_tension=9.0,
        axial_stress=9.0,
        joint_inflammation=3.0,
        cns_fatigue=7.0
    )
    assert sfr_squat == 0.47
    assert sfr_hack > sfr_squat


def test_estimate_exercise_duration_aps_compression():
    """Antagonist paired sets should reduce session duration by ~45%."""
    straight_duration = HypertrophyMathEngine.estimate_exercise_duration(
        sets=3,
        rest_seconds=90,
        is_aps_paired=False
    )
    aps_duration = HypertrophyMathEngine.estimate_exercise_duration(
        sets=3,
        rest_seconds=90,
        is_aps_paired=True
    )
    assert aps_duration < straight_duration
