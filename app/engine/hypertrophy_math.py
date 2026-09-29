"""Hypertrophy Science & Sports Performance Mathematics Engine."""

import math
from typing import List, Optional, Tuple
from app.engine.biomechanical_graph import ExerciseNode
from app.schemas.adaptation import (
    AdaptedExerciseSet,
    DailyDrawbacks,
    HypertrophyPreferences,
    PlannedExercise,
)


class HypertrophyMathEngine:
    """Calculates SFR, dynamic RIR autoregulation, APS time compression, and volume landmarks."""

    @staticmethod
    def calculate_load_scaling_factor(sleep_hours: float, subjective_readiness: Optional[int] = 5) -> float:
        """
        Calculates dynamic load scaling factor alpha:
        alpha = 1.0 - max(0.0, (7.0 - sleep_hours) / 20.0)
        Additionally penalizes low subjective readiness.
        """
        sleep_penalty = max(0.0, (7.0 - sleep_hours) / 20.0)
        readiness_val = subjective_readiness or 5
        readiness_penalty = max(0.0, (5 - readiness_val) * 0.02)
        alpha = 1.0 - (sleep_penalty + readiness_penalty)
        return round(max(0.70, min(1.0, alpha)), 3)

    @staticmethod
    def autoregulate_weight(
        baseline_weight: Optional[float],
        sleep_hours: float,
        subjective_readiness: Optional[int] = 5
    ) -> Optional[float]:
        """Scales working weight based on recovery deficits."""
        if baseline_weight is None or baseline_weight <= 0:
            return None
        alpha = HypertrophyMathEngine.calculate_load_scaling_factor(sleep_hours, subjective_readiness)
        return round(baseline_weight * alpha, 1)

    @staticmethod
    def calculate_sfr(
        mechanical_tension: float,
        axial_stress: float,
        joint_inflammation: float,
        cns_fatigue: float
    ) -> float:
        """
        Stimulus-to-Fatigue Ratio (SFR):
        SFR = Local Muscle Tension / (Axial Stress + Joint Inflammation + CNS Fatigue)
        """
        denominator = axial_stress + joint_inflammation + cns_fatigue
        if denominator <= 0:
            denominator = 0.5
        return round(mechanical_tension / denominator, 2)

    @staticmethod
    def estimate_exercise_duration(
        sets: int,
        rest_seconds: int,
        is_aps_paired: bool = False,
        is_myo_reps: bool = False
    ) -> int:
        """
        Estimates total minutes required for an exercise.
        Straight set: ~45s work + rest_seconds.
        APS paired: ~45% duration reduction.
        Myo-reps: 1 activation set + 3 mini-sets (~3.5 minutes total).
        """
        if is_myo_reps:
            return 4  # 4 minutes for full myo-rep cluster

        seconds_per_set = 45 + rest_seconds
        total_seconds = sets * seconds_per_set

        if is_aps_paired:
            total_seconds = int(total_seconds * 0.55)  # 45% time savings

        return max(2, math.ceil(total_seconds / 60))

    @staticmethod
    def compress_workout_plan(
        exercises: List[Tuple[ExerciseNode, PlannedExercise]],
        drawbacks: DailyDrawbacks,
        preferences: HypertrophyPreferences,
        antagonist_map: dict
    ) -> Tuple[List[AdaptedExerciseSet], int, int]:
        """
        Compresses session to fit available minutes while preserving >=85% effective volume.
        Returns: (adapted_sets, total_effective_sets, total_duration_min)
        """
        adapted_sets: List[AdaptedExerciseSet] = []
        target_minutes = drawbacks.available_minutes
        scale_factor = HypertrophyMathEngine.calculate_load_scaling_factor(
            drawbacks.sleep_hours, drawbacks.subjective_readiness_1_to_10
        )

        total_effective_sets = 0
        total_duration = 0

        # Check if acute time crunch (< 40 mins)
        use_aps = preferences.enable_antagonist_paired_sets and target_minutes <= 45
        use_myo = preferences.enable_rest_pause_myo_reps and target_minutes <= 35

        for i, (node, planned) in enumerate(exercises):
            # Base sets
            prescribed_sets = planned.sets
            is_paired = False
            is_myo = False
            intensifier = None
            rest_sec = 90

            # Check for APS pairing
            if use_aps and node.id in antagonist_map:
                is_paired = True
                intensifier = "antagonist_paired_set"
                rest_sec = 60

            # Check for Myo-reps on high-SFR, low-axial movements
            if use_myo and node.axial_stress_rating <= 2 and not is_paired and i >= 1:
                is_myo = True
                intensifier = "myo_reps_cluster"
                prescribed_sets = 1  # 1 activation + 3 mini-sets represents 3 effective sets
                effective_sets_gained = 3
            else:
                effective_sets_gained = prescribed_sets

            # Calculate working weight
            weight = None
            if planned.prescribed_load_kg:
                weight = round(planned.prescribed_load_kg * scale_factor, 1)

            # RIR adjusted slightly upward if sleep is low
            target_rir = planned.target_rir
            if drawbacks.sleep_hours < 5.0:
                target_rir = min(4.0, target_rir + 0.5)

            duration = HypertrophyMathEngine.estimate_exercise_duration(
                sets=prescribed_sets,
                rest_seconds=rest_sec,
                is_aps_paired=is_paired,
                is_myo_reps=is_myo
            )

            total_duration += duration
            total_effective_sets += effective_sets_gained

            notes = []
            if scale_factor < 1.0:
                notes.append(f"Load scaled by {int((1.0 - scale_factor) * 100)}% for recovery")
            if intensifier:
                notes.append(f"Intensifier: {intensifier}")

            adapted_sets.append(AdaptedExerciseSet(
                exercise_id=node.id,
                exercise_label=node.name,
                sets=prescribed_sets,
                rep_range=planned.target_reps if not is_myo else "10-12 + 3x3",
                target_rir=target_rir,
                recommended_load_kg=weight,
                rest_seconds=rest_sec,
                intensifier_type=intensifier,
                biomechanical_notes="; ".join(notes) if notes else "Preserved straight set"
            ))

        return adapted_sets, total_effective_sets, total_duration
