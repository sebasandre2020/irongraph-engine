"""Schemas for Text-Based Routine Adaptation Agent."""

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from app.schemas.adaptation import DailyDrawbacks, AdaptedExerciseSet, AdaptedWorkout


class ExerciseComparison(BaseModel):
    """Side-by-side comparison between original and adapted exercise."""
    original_name: str
    original_sets: int
    original_reps: str
    original_load: Optional[str] = None
    adapted_name: str
    adapted_sets: int
    adapted_reps: str
    adapted_load: Optional[str] = None
    rest_seconds: int = 90
    status_tag: str = Field(..., description="E.g. PRESERVED, SUBSTITUTED, APS_PAIRED, LOAD_SCALED, MYO_REPS")
    change_rationale: str
    intensifier: Optional[str] = None


class TextAdaptationRequest(BaseModel):
    """Request payload containing raw routine text and daily drawbacks."""
    routine_text: str = Field(..., min_length=5, description="Raw text of the current gym routine")
    selected_day: Optional[str] = Field(default=None, description="Optional day identifier if routine contains multiple days")
    sleep_hours: float = Field(default=5.0, ge=0.0, le=24.0, description="Hours of sleep today")
    baseline_sleep_hours: float = Field(default=8.0, ge=4.0, le=12.0, description="Target baseline sleep")
    available_minutes: int = Field(default=30, ge=10, le=240, description="Minutes available to train today")
    occupied_equipment: List[str] = Field(default_factory=list, description="Unavailable machines or occupied equipment")
    localized_pain_symptoms: List[str] = Field(default_factory=list, description="Pain or joint issues (e.g. lower back, shoulder)")
    subjective_readiness_1_to_10: int = Field(default=5, ge=1, le=10, description="Readiness score")
    preferred_language: str = Field(default="es", description="Language for coaching output: 'es' or 'en'")


class TextAdaptationResponse(BaseModel):
    """Complete response returned to the frontend comparison view."""
    adaptation_id: UUID = Field(default_factory=uuid4)
    detected_day_title: str
    original_exercises_count: int
    adapted_exercises_count: int
    estimated_duration_min: int
    time_saved_min: int
    effective_volume_percentage: float = 100.0
    sfr_rating: str = "VERY_HIGH"
    comparisons: List[ExerciseComparison]
    coaching_rationale: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
