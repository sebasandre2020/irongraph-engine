"""Lifter Management & Workout Autoregulation API."""

from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from sse_starlette.sse import EventSourceResponse

from app.api.deps import get_lifter_store
from app.ai.orchestrator import HypertrophyOrchestrator
from app.schemas.lifter import CreateLifterRequest, LifterResponse
from app.schemas.adaptation import AdaptationRequest, AdaptationResponse

router = APIRouter(prefix="/v1/lifters", tags=["Lifters & Adaptations"])
orchestrator = HypertrophyOrchestrator()


@router.post("", response_model=LifterResponse, status_code=status.HTTP_201_CREATED, summary="Register Lifter Profile")
async def create_lifter(
    payload: CreateLifterRequest,
    store: dict = Depends(get_lifter_store)
):
    """Initializes a new lifter profile with volume landmarks and baseline metrics."""
    new_id = uuid4()
    profile = LifterResponse(
        id=new_id,
        name=payload.name,
        experience_tier=payload.experience_tier,
        volume_landmarks=payload.volume_landmarks,
        baseline_1rms=payload.baseline_1rms,
        active_contraindications=payload.active_contraindications
    )
    store[new_id] = profile
    return profile


@router.get("/{lifter_id}", response_model=LifterResponse, summary="Get Lifter Profile")
async def get_lifter(
    lifter_id: UUID,
    store: dict = Depends(get_lifter_store)
):
    """Retrieves lifter profile, active contraindications, and volume landmarks."""
    if lifter_id not in store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lifter '{lifter_id}' not found"
        )
    return store[lifter_id]


@router.post("/{lifter_id}/adapt", summary="Adapt Workout to Atypical Friction")
async def adapt_workout(
    lifter_id: UUID,
    payload: AdaptationRequest,
    request: Request,
    accept: str = Header(default="application/json"),
    store: dict = Depends(get_lifter_store)
):
    """
    Autoregulates planned workout session according to daily drawbacks.
    Emits Server-Sent Events (SSE) if Accept: text/event-stream is requested.
    """
    if lifter_id not in store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lifter '{lifter_id}' not found"
        )
    lifter = store[lifter_id]

    if "text/event-stream" in accept:
        async def event_generator():
            async for chunk in orchestrator.stream_adaptation(lifter, payload):
                yield chunk
        return EventSourceResponse(event_generator())

    response = await orchestrator.adapt_workout(lifter, payload)
    return response
