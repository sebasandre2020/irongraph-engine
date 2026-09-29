"""Health check schemas."""

from typing import Dict, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class HealthStatus(BaseModel):
    """Health check response status."""
    status: str = Field(..., description="Service status: alive, ready, or degraded")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp"
    )
    version: str = Field(default="0.1.0", description="Application semantic version")
    dependencies: Optional[Dict[str, str]] = Field(
        default=None,
        description="Status of connected dependencies (postgres, redis, qdrant)"
    )
