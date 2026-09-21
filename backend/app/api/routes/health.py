"""Health check route."""

from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = "Yojana Sahayak"
    version: str = "0.1.0"
    environment: str = "development"
    timestamp: str


@router.get("/health", response_model=HealthResponse, summary="Service Health Check")
async def health_check() -> HealthResponse:
    """Health check endpoint to verify backend service operational readiness."""
    return HealthResponse(
        status="healthy",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.APP_ENV,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
