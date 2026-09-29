"""Pytest fixtures for IronGraph-Engine."""

import pytest
from uuid import UUID
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import SEED_LIFTER_ID


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_lifter_id() -> UUID:
    """Canonical test lifter UUID."""
    return SEED_LIFTER_ID
