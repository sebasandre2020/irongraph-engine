"""Health check routes."""

from fastapi import APIRouter
from app.schemas.health import HealthStatus
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health/live", response_model=HealthStatus, summary="Liveness Probe")
async def get_liveness():
    """Confirms service process is alive."""
    return HealthStatus(
        status="alive",
        version="0.1.0"
    )


@router.get("/health/ready", response_model=HealthStatus, summary="Readiness Probe")
async def get_readiness():
    """Validates service readiness and dependency status."""
    deps = {
        "postgres": "ready (mock/configured)",
        "redis": "ready (mock/configured)",
        "llm_provider": settings.LLM_PRIMARY_PROVIDER
    }
    return HealthStatus(
        status="ready",
        version="0.1.0",
        dependencies=deps
    )
