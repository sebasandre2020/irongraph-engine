"""Agent API Router for Free-Form Routine Adaptation."""

import os
from fastapi import APIRouter, HTTPException, status
from app.ai.agent_service import agent_service
from app.schemas.routine_agent import (
    TextAdaptationRequest,
    TextAdaptationResponse,
)
from app.engine.routine_parser import extract_day_sections

router = APIRouter(prefix="/v1/agent", tags=["Personal Hypertrophy Agent"])

GYM_ROUTINE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "GymRutine.txt")


@router.post("/adapt-routine", response_model=TextAdaptationResponse, summary="Adapt Free-Form Gym Routine to Daily Drawbacks")
async def adapt_routine_endpoint(request: TextAdaptationRequest):
    """
    Consumes a plain-text gym routine and adjusts it based on daily drawbacks:
    sleep deficits, time availability, machine blockers, and pain symptoms.
    Returns side-by-side exercise comparison and coaching rationale.
    """
    try:
        response = await agent_service.adapt_routine(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Routine adaptation error: {str(e)}"
        )


@router.get("/example-routine", summary="Get Preloaded Gym Routine Example")
async def get_example_routine():
    """Returns the text from GymRutine.txt and available day sections."""
    if not os.path.exists(GYM_ROUTINE_PATH):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GymRutine.txt not found"
        )

    with open(GYM_ROUTINE_PATH, "r", encoding="utf-8") as f:
        full_text = f.read()

    days = extract_day_sections(full_text)
    day_options = [
        {
            "day_id": d.day_id,
            "title": d.title,
            "exercise_count": len(d.exercises),
            "exercises": [ex.name for ex in d.exercises]
        }
        for d in days
    ]

    return {
        "filename": "GymRutine.txt",
        "full_text": full_text,
        "available_days": day_options
    }
