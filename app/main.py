"""FastAPI Application Entrypoint for IronGraph-Engine."""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.health import router as health_router
from app.api.v1.lifters import router as lifters_router
from app.api.v1.exercises import router as exercises_router
from app.api.v1.agent import router as agent_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("irongraph")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
INDEX_PATH = os.path.join(STATIC_DIR, "index.html")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan handler."""
    logger.info("Initializing IronGraph-Engine Autoregulation Subsystems...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Primary LLM Provider: {settings.LLM_PRIMARY_PROVIDER}")
    logger.info(f"Target Service Port: {settings.PORT}")
    yield
    logger.info("Shutting down IronGraph-Engine Subsystems...")


app = FastAPI(
    title="IronGraph-Engine Headless API",
    description="Personal Hypertrophy Assistant & Workout Autoregulation Service",
    version="0.2.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(health_router)
app.include_router(lifters_router)
app.include_router(exercises_router)
app.include_router(agent_router)

# Mount Static Files & Home Page
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", summary="Frontend Personal Hypertrophy Assistant UI")
async def get_frontend():
    """Serves the dual-pane testing frontend."""
    if os.path.exists(INDEX_PATH):
        return FileResponse(INDEX_PATH, media_type="text/html")
    return {"message": "IronGraph Engine API is running. UI not found.", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
