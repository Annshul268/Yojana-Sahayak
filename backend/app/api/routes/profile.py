"""Citizen Profile REST API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.connection import get_db
from backend.app.database.models import UserProfile
from backend.app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=ProfileResponse, summary="Get Citizen Profile")
async def get_profile(
    user_id: str = Query(..., description="Unique citizen/user identifier"),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    stmt = select(UserProfile).where(UserProfile.user_id == user_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found for this citizen")
    return ProfileResponse.model_validate(profile)


@router.post("", response_model=ProfileResponse, summary="Create or Update Citizen Profile")
async def upsert_profile(
    payload: ProfileCreate,
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    stmt = select(UserProfile).where(UserProfile.user_id == payload.user_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    if profile:
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(profile, k, v)
    else:
        profile = UserProfile(**payload.model_dump())
        db.add(profile)

    await db.commit()
    await db.refresh(profile)
    return ProfileResponse.model_validate(profile)
