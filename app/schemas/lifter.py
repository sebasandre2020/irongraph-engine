"""Lifter Profile schemas."""

from typing import Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class VolumeLandmark(BaseModel):
    """Muscle-specific volume landmarks in weekly sets."""
    mev: int = Field(..., ge=0, description="Minimum Effective Volume")
    mav: int = Field(..., ge=0, description="Maximum Adaptive Volume")
    mrv: int = Field(..., ge=0, description="Maximum Recoverable Volume")


class CreateLifterRequest(BaseModel):
    """Payload to register a new lifter profile."""
    name: str = Field(..., min_length=1, max_length=255)
    experience_tier: str = Field(
        default="intermediate",
        description="Experience tier: beginner, intermediate, or advanced"
    )
    volume_landmarks: Dict[str, VolumeLandmark] = Field(
        default_factory=lambda: {
            "chest": VolumeLandmark(mev=8, mav=14, mrv=20),
            "back": VolumeLandmark(mev=10, mav=16, mrv=22),
            "quads": VolumeLandmark(mev=8, mav=12, mrv=18),
            "hamstrings": VolumeLandmark(mev=6, mav=10, mrv=14)
        }
    )
    baseline_1rms: Dict[str, float] = Field(
        default_factory=dict,
        description="Baseline 1-Rep-Max values in kilograms"
    )
    active_contraindications: List[str] = Field(
        default_factory=list,
        description="Active joint issues or symptoms (e.g., acute_lumbar_strain)"
    )


class LifterResponse(BaseModel):
    """Retrieved lifter profile representation."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    experience_tier: str
    volume_landmarks: Dict[str, VolumeLandmark]
    baseline_1rms: Dict[str, float]
    active_contraindications: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
