"""Schemas registry."""

from app.schemas.health import HealthStatus
from app.schemas.lifter import CreateLifterRequest, LifterResponse, VolumeLandmark
from app.schemas.adaptation import (
    DailyDrawbacks,
    HypertrophyPreferences,
    AdaptedExerciseSet,
    AdaptedWorkout,
    AdaptationRequest,
    AdaptationResponse,
    PlannedWorkout,
    PlannedExercise,
)
from app.schemas.exercise import (
    ExerciseSubstitute,
    ExerciseSubstitutionRequest,
    ExerciseSubstitutionResponse,
)

__all__ = [
    "HealthStatus",
    "CreateLifterRequest",
    "LifterResponse",
    "VolumeLandmark",
    "DailyDrawbacks",
    "HypertrophyPreferences",
    "AdaptedExerciseSet",
    "AdaptedWorkout",
    "AdaptationRequest",
    "AdaptationResponse",
    "PlannedWorkout",
    "PlannedExercise",
    "ExerciseSubstitute",
    "ExerciseSubstitutionRequest",
    "ExerciseSubstitutionResponse",
]
