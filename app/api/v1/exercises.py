"""Exercise Substitution API."""

from fastapi import APIRouter, HTTPException, status
from app.engine.biomechanical_graph import default_graph
from app.schemas.exercise import (
    ExerciseSubstitute,
    ExerciseSubstitutionRequest,
    ExerciseSubstitutionResponse,
)

router = APIRouter(prefix="/v1/exercises", tags=["Biomechanical Exercises"])


@router.post("/substitute", response_model=ExerciseSubstitutionResponse, summary="1:1 Biomechanical Exercise Substitution")
async def substitute_exercise(payload: ExerciseSubstitutionRequest):
    """
    Finds biomechanically compatible exercise substitutes matching target movement patterns
    while respecting equipment constraints and spinal axial thresholds.
    """
    origin = default_graph.get_exercise(payload.exercise_id)
    if not origin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise '{payload.exercise_id}' not found in taxonomy"
        )

    # Filter substitutes
    candidates = default_graph.find_substitutes(
        exercise_id=payload.exercise_id,
        available_equipment=payload.available_equipment,
        max_axial=payload.max_axial_stress
    )

    substitutes = []
    for cand in candidates:
        rationale = f"Matches {cand.movement_pattern} pattern with SFR {cand.sfr_rating} and axial stress {cand.axial_stress_rating}/10."
        if cand.axial_stress_rating < origin.axial_stress_rating:
            rationale += f" Reduces axial loading by {origin.axial_stress_rating - cand.axial_stress_rating} points."
        substitutes.append(ExerciseSubstitute(
            exercise_id=cand.id,
            exercise_name=cand.name,
            movement_pattern=cand.movement_pattern,
            axial_stress_rating=cand.axial_stress_rating,
            sfr_rating=cand.sfr_rating,
            required_equipment=cand.required_equipment,
            substitution_rationale=rationale
        ))

    return ExerciseSubstitutionResponse(
        original_exercise_id=payload.exercise_id,
        substitutes=substitutes
    )
