"""Workout Autoregulation Orchestrator with Streaming & Verification."""

import json
from typing import AsyncIterator, Dict, Any, List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.engine.biomechanical_graph import BiomechanicalGraph, ExerciseNode, default_graph
from app.engine.rule_engine import BiomechanicalRuleEngine
from app.engine.hypertrophy_math import HypertrophyMathEngine
from app.ai.adapters import BaseLLMAdapter, LLMAdapterFactory
from app.schemas.lifter import LifterResponse
from app.schemas.adaptation import (
    AdaptationRequest,
    AdaptationResponse,
    AdaptedWorkout,
    DailyDrawbacks,
    HypertrophyPreferences,
    PlannedExercise,
    PlannedWorkout,
)


class HypertrophyOrchestrator:
    """Orchestrates biomechanical graph pruning, math compression, and LLM rationale."""

    def __init__(self, graph: Optional[BiomechanicalGraph] = None, llm_adapter: Optional[BaseLLMAdapter] = None):
        self.graph = graph or default_graph
        self.rule_engine = BiomechanicalRuleEngine(self.graph)
        self.llm_adapter = llm_adapter or LLMAdapterFactory.get_adapter()

    def _prepare_pipeline(
        self,
        lifter: LifterResponse,
        request: AdaptationRequest
    ) -> Dict[str, Any]:
        drawbacks = request.drawbacks
        preferences = request.hypertrophy_preferences or HypertrophyPreferences()

        # Build or use planned workout
        planned = request.planned_workout or PlannedWorkout(
            title="Standard Lower/Upper Regimen",
            target_duration_min=60,
            exercises=[
                PlannedExercise(exercise_id="barbell_back_squat", sets=3, target_reps="6-8", prescribed_load_kg=120.0),
                PlannedExercise(exercise_id="incline_dumbbell_press", sets=3, target_reps="8-10", prescribed_load_kg=38.0),
                PlannedExercise(exercise_id="barbell_bent_over_row", sets=3, target_reps="8-10", prescribed_load_kg=85.0),
            ]
        )

        # 1. Biomechanical Graph Pruning & Substitution
        available_equipment = [
            eq for eq in ["squat_rack", "hack_squat_machine", "leg_press_machine", "dumbbells", "tbar_machine", "barbell", "leg_curl_machine"]
            if eq not in drawbacks.occupied_equipment
        ]

        substituted_exercises = []
        substitution_reasons = []

        for item in planned.exercises:
            safe_node, note = self.rule_engine.prune_and_substitute(
                exercise_id=item.exercise_id,
                drawbacks=drawbacks,
                active_contraindications=lifter.active_contraindications,
                available_equipment=available_equipment
            )
            substituted_exercises.append((safe_node, item))
            if note:
                substitution_reasons.append(note)

        # 2. Map Antagonist Pairs
        antagonist_map = {}
        for node, _ in substituted_exercises:
            pairs = self.graph.get_antagonist_pairs(node.id)
            if pairs:
                antagonist_map[node.id] = pairs

        # 3. Hypertrophy Math Compression
        adapted_sets, total_effective_sets, total_duration = HypertrophyMathEngine.compress_workout_plan(
            exercises=substituted_exercises,
            drawbacks=drawbacks,
            preferences=preferences,
            antagonist_map=antagonist_map
        )

        # Planned effective sets
        planned_effective_sets = sum(ex.sets for ex in planned.exercises)
        volume_delta = total_effective_sets - planned_effective_sets

        adapted_workout = AdaptedWorkout(
            title=f"Adapted Hypertrophy: Express Autoregulated Session ({total_duration} min)",
            estimated_duration_min=total_duration,
            total_effective_sets=total_effective_sets,
            sfr_rating="VERY_HIGH" if drawbacks.sleep_hours < 5.0 else "HIGH",
            exercises=adapted_sets
        )

        return {
            "adapted_workout": adapted_workout,
            "substitution_reasons": substitution_reasons,
            "volume_delta": volume_delta,
            "drawbacks": drawbacks.model_dump(),
        }

    async def adapt_workout(
        self,
        lifter: LifterResponse,
        request: AdaptationRequest
    ) -> AdaptationResponse:
        """Executes full non-streaming adaptation."""
        pipeline = self._prepare_pipeline(lifter, request)
        adapted_workout = pipeline["adapted_workout"]

        coaching_prose = await self.llm_adapter.generate_coaching_rationale(
            lifter_name=lifter.name,
            drawbacks=pipeline["drawbacks"],
            adapted_exercises=[ex.model_dump() for ex in adapted_workout.exercises],
            volume_delta=pipeline["volume_delta"]
        )

        return AdaptationResponse(
            adaptation_id=uuid4(),
            lifter_id=lifter.id,
            status="COMMITTED",
            adapted_workout=adapted_workout,
            coaching_prose=coaching_prose,
            effective_volume_delta=pipeline["volume_delta"],
            committed_at=datetime.now(timezone.utc)
        )

    async def stream_adaptation(
        self,
        lifter: LifterResponse,
        request: AdaptationRequest
    ) -> AsyncIterator[Dict[str, Any]]:
        """Yields Server-Sent Events (SSE) chunks: token, workout_delta, complete."""
        pipeline = self._prepare_pipeline(lifter, request)
        adapted_workout = pipeline["adapted_workout"]
        adaptation_id = uuid4()

        # Stream tokens
        async for token in self.llm_adapter.stream_coaching_tokens(
            lifter_name=lifter.name,
            drawbacks=pipeline["drawbacks"],
            adapted_exercises=[ex.model_dump() for ex in adapted_workout.exercises],
            volume_delta=pipeline["volume_delta"]
        ):
            yield {
                "event": "token",
                "data": json.dumps({"text": token})
            }

        # Emit structured workout delta
        yield {
            "event": "workout_delta",
            "data": json.dumps(adapted_workout.model_dump(), default=str)
        }

        # Emit completion frame
        yield {
            "event": "complete",
            "data": json.dumps({
                "adaptation_id": str(adaptation_id),
                "status": "COMMITTED"
            })
        }
