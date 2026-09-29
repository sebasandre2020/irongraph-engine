"""Exercise substitution schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ExerciseSubstitute(BaseModel):
    """A matching biomechanical exercise substitute."""
    exercise_id: str
    exercise_name: str
    movement_pattern: str
    axial_stress_rating: int
    sfr_rating: str
    required_equipment: str
    substitution_rationale: str


class ExerciseSubstitutionRequest(BaseModel):
    """Payload to query 1:1 biomechanical exercise substitution."""
    exercise_id: str
    available_equipment: List[str]
    max_axial_stress: Optional[int] = Field(default=None, ge=0, le=10)
    symptoms: Optional[List[str]] = Field(default_factory=list)


class ExerciseSubstitutionResponse(BaseModel):
    """Response containing substitute recommendations."""
    original_exercise_id: str
    substitutes: List[ExerciseSubstitute]
