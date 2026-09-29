"""API Dependencies & Lifter Store."""

from typing import Dict
from uuid import UUID
from app.schemas.lifter import LifterResponse, VolumeLandmark

# Thread-safe in-memory lifter store seeded with test profile matching 001_init_schema.sql
SEED_LIFTER_ID = UUID("f1e2d3c4-b5a6-7890-1234-567890abcdef")

_LIFTER_STORE: Dict[UUID, LifterResponse] = {
    SEED_LIFTER_ID: LifterResponse(
        id=SEED_LIFTER_ID,
        name="Alex Turner",
        experience_tier="advanced",
        volume_landmarks={
            "chest": VolumeLandmark(mev=8, mav=14, mrv=20),
            "back": VolumeLandmark(mev=10, mav=16, mrv=22),
            "quads": VolumeLandmark(mev=8, mav=12, mrv=18),
            "hamstrings": VolumeLandmark(mev=6, mav=10, mrv=14),
        },
        baseline_1rms={
            "barbell_back_squat": 160.0,
            "incline_dumbbell_press": 42.0,
            "barbell_bent_over_row": 110.0
        },
        active_contraindications=["acute_lumbar_strain"]
    )
}


def get_lifter_store() -> Dict[UUID, LifterResponse]:
    """Provides the lifter profile store."""
    return _LIFTER_STORE
