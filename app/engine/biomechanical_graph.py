"""Biomechanical Property Graph Engine."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import networkx as nx


class ExerciseNode(BaseModel):
    """Exercise node representation in the biomechanical graph."""
    id: str
    name: str
    movement_pattern: str
    primary_muscles: List[str]
    secondary_muscles: List[str] = Field(default_factory=list)
    axial_stress_rating: int = Field(..., ge=0, le=10)
    required_equipment: str
    sfr_rating: str = "high"
    resistance_curve_focus: str = "mid_range"
    is_unilateral: bool = False


# Canonical seed exercises matching infra/postgres/001_init_schema.sql
SEED_EXERCISES: Dict[str, ExerciseNode] = {
    "barbell_back_squat": ExerciseNode(
        id="barbell_back_squat",
        name="Barbell Back Squat",
        movement_pattern="squat",
        primary_muscles=["quads", "glutes"],
        secondary_muscles=["adductors", "spinal_erectors"],
        axial_stress_rating=9,
        required_equipment="squat_rack",
        sfr_rating="moderate",
        resistance_curve_focus="mid_range"
    ),
    "hack_squat": ExerciseNode(
        id="hack_squat",
        name="Machine Hack Squat",
        movement_pattern="squat",
        primary_muscles=["quads"],
        secondary_muscles=["glutes"],
        axial_stress_rating=3,
        required_equipment="hack_squat_machine",
        sfr_rating="very_high",
        resistance_curve_focus="lengthened"
    ),
    "leg_press": ExerciseNode(
        id="leg_press",
        name="45-Degree Leg Press",
        movement_pattern="squat",
        primary_muscles=["quads"],
        secondary_muscles=["glutes"],
        axial_stress_rating=2,
        required_equipment="leg_press_machine",
        sfr_rating="high",
        resistance_curve_focus="mid_range"
    ),
    "incline_dumbbell_press": ExerciseNode(
        id="incline_dumbbell_press",
        name="Incline Dumbbell Bench Press",
        movement_pattern="horizontal_press",
        primary_muscles=["upper_chest"],
        secondary_muscles=["anterior_deltoid", "triceps"],
        axial_stress_rating=1,
        required_equipment="dumbbells",
        sfr_rating="very_high",
        resistance_curve_focus="lengthened"
    ),
    "chest_supported_tbar_row": ExerciseNode(
        id="chest_supported_tbar_row",
        name="Chest-Supported T-Bar Row",
        movement_pattern="horizontal_pull",
        primary_muscles=["lats", "rhomboids"],
        secondary_muscles=["biceps", "rear_delts"],
        axial_stress_rating=1,
        required_equipment="tbar_machine",
        sfr_rating="very_high",
        resistance_curve_focus="lengthened"
    ),
    "barbell_bent_over_row": ExerciseNode(
        id="barbell_bent_over_row",
        name="Barbell Bent-Over Row",
        movement_pattern="horizontal_pull",
        primary_muscles=["lats", "upper_back"],
        secondary_muscles=["spinal_erectors", "biceps"],
        axial_stress_rating=7,
        required_equipment="barbell",
        sfr_rating="moderate",
        resistance_curve_focus="mid_range"
    ),
    "seated_leg_curl": ExerciseNode(
        id="seated_leg_curl",
        name="Seated Hamstring Leg Curl",
        movement_pattern="knee_flexion",
        primary_muscles=["hamstrings"],
        secondary_muscles=["gastrocnemius"],
        axial_stress_rating=0,
        required_equipment="leg_curl_machine",
        sfr_rating="very_high",
        resistance_curve_focus="lengthened"
    ),
    "romanian_deadlift": ExerciseNode(
        id="romanian_deadlift",
        name="Barbell Romanian Deadlift",
        movement_pattern="hinge",
        primary_muscles=["hamstrings", "glutes"],
        secondary_muscles=["spinal_erectors"],
        axial_stress_rating=8,
        required_equipment="barbell",
        sfr_rating="high",
        resistance_curve_focus="lengthened"
    )
}

SEED_EDGES = [
    ("barbell_back_squat", "hack_squat", "substitute_for", {"reason": "lowers_axial_stress_preserves_quad_tension"}),
    ("barbell_back_squat", "leg_press", "substitute_for", {"reason": "eliminates_spinal_loading"}),
    ("barbell_bent_over_row", "chest_supported_tbar_row", "substitute_for", {"reason": "eliminates_lower_back_fatigue"}),
    ("incline_dumbbell_press", "chest_supported_tbar_row", "antagonist_pair_with", {"antagonist_plane": "horizontal_push_pull", "time_savings_pct": 45}),
    ("hack_squat", "seated_leg_curl", "antagonist_pair_with", {"antagonist_plane": "quad_hamstring_pair", "time_savings_pct": 40}),
]


class BiomechanicalGraph:
    """In-memory property graph wrapper for exercise taxonomy and safety evaluation."""

    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.exercises: Dict[str, ExerciseNode] = {}
        self._load_seed_graph()

    def _load_seed_graph(self):
        for ex_id, node in SEED_EXERCISES.items():
            self.exercises[ex_id] = node
            self.graph.add_node(ex_id, **node.model_dump())

        for src, dst, rel, props in SEED_EDGES:
            self.graph.add_edge(src, dst, relation=rel, **props)

    def get_exercise(self, exercise_id: str) -> Optional[ExerciseNode]:
        return self.exercises.get(exercise_id)

    def get_axial_stress_score(self, exercise_id: str) -> int:
        ex = self.get_exercise(exercise_id)
        return ex.axial_stress_rating if ex else 0

    def find_substitutes(
        self,
        exercise_id: str,
        available_equipment: List[str],
        max_axial: Optional[int] = None
    ) -> List[ExerciseNode]:
        """Find matching exercise substitutes by pattern, equipment, and axial constraint."""
        origin = self.get_exercise(exercise_id)
        if not origin:
            return []

        substitutes: List[ExerciseNode] = []

        # 1. First check explicit graph edges
        if self.graph.has_node(exercise_id):
            for _, target, data in self.graph.out_edges(exercise_id, data=True):
                if data.get("relation") == "substitute_for":
                    target_ex = self.get_exercise(target)
                    if target_ex and (not available_equipment or target_ex.required_equipment in available_equipment):
                        if max_axial is None or target_ex.axial_stress_rating <= max_axial:
                            substitutes.append(target_ex)

        # 2. Also check same movement pattern & primary muscle targets
        for ex_id, candidate in self.exercises.items():
            if ex_id == exercise_id or candidate in substitutes:
                continue
            if candidate.movement_pattern == origin.movement_pattern:
                # Check muscle overlap
                has_muscle_overlap = any(m in candidate.primary_muscles for m in origin.primary_muscles)
                if has_muscle_overlap:
                    equipment_ok = not available_equipment or candidate.required_equipment in available_equipment
                    axial_ok = max_axial is None or candidate.axial_stress_rating <= max_axial
                    if equipment_ok and axial_ok:
                        substitutes.append(candidate)

        # Sort by axial stress ascending (lower spinal fatigue first) then sfr_rating
        substitutes.sort(key=lambda x: (x.axial_stress_rating, 0 if x.sfr_rating == "very_high" else 1))
        return substitutes

    def get_antagonist_pairs(self, exercise_id: str) -> List[str]:
        """Get exercise IDs that can be paired as antagonist paired sets (APS)."""
        pairs: List[str] = []
        if self.graph.has_node(exercise_id):
            for _, target, data in self.graph.out_edges(exercise_id, data=True):
                if data.get("relation") == "antagonist_pair_with":
                    pairs.append(target)
            for src, _, data in self.graph.in_edges(exercise_id, data=True):
                if data.get("relation") == "antagonist_pair_with":
                    pairs.append(src)
        return list(set(pairs))


default_graph = BiomechanicalGraph()
