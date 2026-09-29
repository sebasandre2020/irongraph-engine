"""Workout adaptation and autoregulation schemas."""

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class DailyDrawbacks(BaseModel):
    """Daily friction and drawbacks experienced by the lifter."""
    sleep_hours: float = Field(..., ge=0.0, le=24.0, description="Hours of sleep obtained")
    available_minutes: int = Field(..., ge=10, le=240, description="Available session duration in minutes")
    occupied_equipment: List[str] = Field(default_factory=list, description="List of blocked equipment identifiers")
    localized_pain_symptoms: List[str] = Field(default_factory=list, description="Reported pain or tightness areas")
    subjective_readiness_1_to_10: Optional[int] = Field(default=5, ge=1, le=10, description="Subjective readiness rating")


class HypertrophyPreferences(BaseModel):
    """Hypertrophy optimization preferences."""
    enable_antagonist_paired_sets: bool = Field(default=True)
    enable_rest_pause_myo_reps: bool = Field(default=True)
    target_rir_buffer: float = Field(default=1.5, ge=0.0, le=5.0)
    preserve_effective_volume: bool = Field(default=True)


class AdaptedExerciseSet(BaseModel):
    """A prescribed exercise set within an adapted workout session."""
    exercise_id: str
    exercise_label: str
    sets: int = Field(..., ge=1)
    rep_range: str
    target_rir: float = Field(..., ge=0.0, le=5.0)
    recommended_load_kg: Optional[float] = None
    rest_seconds: Optional[int] = 90
    intensifier_type: Optional[str] = None
    biomechanical_notes: Optional[str] = None


class AdaptedWorkout(BaseModel):
    """Full adapted workout structure."""
    title: str
    estimated_duration_min: int = Field(..., ge=1)
    total_effective_sets: int = Field(..., ge=1)
    sfr_rating: str = Field(default="HIGH")
    exercises: List[AdaptedExerciseSet]


class PlannedExercise(BaseModel):
    """Planned exercise definition."""
    exercise_id: str
    sets: int = 3
    target_reps: str = "8-10"
    target_rir: float = 2.0
    prescribed_load_kg: Optional[float] = None


class PlannedWorkout(BaseModel):
    """Planned workout blueprint."""
    title: str = "Planned Hypertrophy Session"
    target_duration_min: int = 60
    exercises: List[PlannedExercise] = Field(default_factory=list)


class AdaptationRequest(BaseModel):
    """Payload to request real-time session adaptation."""
    planned_workout_id: Optional[UUID] = None
    planned_workout: Optional[PlannedWorkout] = None
    drawbacks: DailyDrawbacks
    hypertrophy_preferences: Optional[HypertrophyPreferences] = Field(default_factory=HypertrophyPreferences)


class AdaptationResponse(BaseModel):
    """Complete adapted workout response."""
    adaptation_id: UUID = Field(default_factory=uuid4)
    lifter_id: UUID
    status: str = "COMMITTED"
    adapted_workout: AdaptedWorkout
    coaching_prose: str
    effective_volume_delta: int = 0
    committed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
