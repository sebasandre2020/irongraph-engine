"""Deterministic Biomechanical Rule Engine."""

from typing import List, Tuple
from app.engine.biomechanical_graph import BiomechanicalGraph, ExerciseNode
from app.schemas.adaptation import DailyDrawbacks


class BiomechanicalRuleEngine:
    """Evaluates safety constraints and prunes contraindicated exercises."""

    def __init__(self, graph: BiomechanicalGraph):
        self.graph = graph

    def evaluate_axial_safety(self, exercise: ExerciseNode, drawbacks: DailyDrawbacks) -> Tuple[bool, str]:
        """
        SpinalCompressiveThresholdRule:
        If sleep is under 5.0 hours or readiness <= 4, prune axial stress >= 7.
        """
        if drawbacks.sleep_hours < 5.0 or (drawbacks.subjective_readiness_1_to_10 and drawbacks.subjective_readiness_1_to_10 <= 4):
            if exercise.axial_stress_rating >= 7:
                return False, f"High axial stress ({exercise.axial_stress_rating}/10) contraindicated under sleep deprivation ({drawbacks.sleep_hours}h)"
        return True, ""

    def evaluate_contraindications(
        self,
        exercise: ExerciseNode,
        drawbacks: DailyDrawbacks,
        active_contraindications: List[str]
    ) -> Tuple[bool, str]:
        """
        ContraindicationPruningRule:
        Evaluate active symptoms or clinical contraindications (e.g. acute lumbar strain).
        """
        all_symptoms = set(active_contraindications + drawbacks.localized_pain_symptoms)
        
        # Lower back / lumbar constraints
        if any("lumbar" in s or "lower_back" in s for s in all_symptoms):
            if exercise.axial_stress_rating >= 6 or "spinal_erectors" in exercise.secondary_muscles:
                return False, f"Exercise exerts lumbar strain ({exercise.axial_stress_rating}/10) contraindicated for lower back symptoms"

        # Knee / patellar constraints
        if any("knee" in s or "patellar" in s for s in all_symptoms):
            if exercise.movement_pattern == "squat" and exercise.axial_stress_rating >= 8:
                return False, "Heavy axial squat contraindicated for knee symptoms"

        return True, ""

    def evaluate_equipment(self, exercise: ExerciseNode, drawbacks: DailyDrawbacks) -> Tuple[bool, str]:
        """
        EquipmentAvailabilityRule:
        Checks if required equipment is occupied or unavailable.
        """
        if exercise.required_equipment in drawbacks.occupied_equipment:
            return False, f"Required equipment '{exercise.required_equipment}' is currently occupied"
        return True, ""

    def is_safe(
        self,
        exercise: ExerciseNode,
        drawbacks: DailyDrawbacks,
        active_contraindications: List[str]
    ) -> Tuple[bool, str]:
        """Run all safety rules on an exercise."""
        safe, reason = self.evaluate_equipment(exercise, drawbacks)
        if not safe:
            return False, reason

        safe, reason = self.evaluate_axial_safety(exercise, drawbacks)
        if not safe:
            return False, reason

        safe, reason = self.evaluate_contraindications(exercise, drawbacks, active_contraindications)
        if not safe:
            return False, reason

        return True, "Safe"

    def prune_and_substitute(
        self,
        exercise_id: str,
        drawbacks: DailyDrawbacks,
        active_contraindications: List[str],
        available_equipment: List[str]
    ) -> Tuple[ExerciseNode, str]:
        """
        Check if exercise is safe; if not, deterministically find a safe substitute.
        """
        origin = self.graph.get_exercise(exercise_id)
        if not origin:
            raise ValueError(f"Exercise ID '{exercise_id}' not found in biomechanical taxonomy")

        safe, reason = self.is_safe(origin, drawbacks, active_contraindications)
        if safe:
            return origin, ""

        # Find safe substitute
        max_axial = 4 if (drawbacks.sleep_hours < 5.0 or any("lumbar" in s or "lower_back" in s for s in active_contraindications + drawbacks.localized_pain_symptoms)) else None
        
        # Equipment available is anything not in occupied_equipment
        candidates = self.graph.find_substitutes(
            exercise_id=exercise_id,
            available_equipment=available_equipment,
            max_axial=max_axial
        )

        for candidate in candidates:
            cand_safe, _ = self.is_safe(candidate, drawbacks, active_contraindications)
            if cand_safe:
                return candidate, f"Substituted '{origin.name}' -> '{candidate.name}': {reason}"

        # If no candidates met all criteria, return origin with warning
        return origin, f"Warning: {reason}, but no safe substitute found"
