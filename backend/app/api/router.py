"""Centralized API Router for Yojana Sahayak."""

from fastapi import APIRouter
from backend.app.api.routes import (
    admin,
    ai,
    health,
    matching,
    profile,
    saved,
    schemes,
    tracking,
)

api_router = APIRouter()

# Register routes
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(matching.router)
api_router.include_router(schemes.router)
api_router.include_router(profile.router)
api_router.include_router(saved.router)
api_router.include_router(tracking.router)
api_router.include_router(ai.router)
api_router.include_router(admin.router)
