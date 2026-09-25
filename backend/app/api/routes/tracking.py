"""Application Tracking REST API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.app.database.connection import get_db
from backend.app.database.models import Scheme, SchemeTracking
from backend.app.schemas.tracking import (
    SchemeTrackingCreate,
    SchemeTrackingResponse,
    SchemeTrackingUpdate,
)

router = APIRouter(tags=["Application Tracking"])

VALID_STATUSES = [
    "Saved",
    "Planning to Apply",
    "Application Started",
    "Applied",
    "Application Submitted",
    "Completed",
]


@router.get("", response_model=List[SchemeTrackingResponse], summary="List Citizen Application Trackers")
async def list_tracking(
    user_id: str = Query(..., description="Unique citizen identifier"),
    db: AsyncSession = Depends(get_db),
) -> List[SchemeTrackingResponse]:
    if not user_id:
        return []
    stmt = (
        select(SchemeTracking)
        .where(SchemeTracking.user_id == user_id)
        .options(selectinload(SchemeTracking.scheme))
        .order_by(SchemeTracking.updated_at.desc(), SchemeTracking.created_at.desc())
    )
    result = await db.execute(stmt)
    entries = result.scalars().all()
    return [SchemeTrackingResponse.model_validate(e) for e in entries]


@router.post("", response_model=SchemeTrackingResponse, summary="Add Application Tracking Entry")
async def create_tracking(
    payload: SchemeTrackingCreate,
    db: AsyncSession = Depends(get_db),
) -> SchemeTrackingResponse:
    if payload.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{payload.status}'. Must be one of: {', '.join(VALID_STATUSES)}",
        )

    # Check existing to prevent duplicates
    stmt = select(SchemeTracking).where(
        SchemeTracking.user_id == payload.user_id,
        SchemeTracking.scheme_id == payload.scheme_id,
    ).options(selectinload(SchemeTracking.scheme))
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        return SchemeTrackingResponse.model_validate(existing)

    from backend.app.database.models import utcnow
    entry_dict = payload.model_dump()
    if entry_dict.get("status") in ("Applied", "Application Submitted"):
        entry_dict["applied_at"] = utcnow()

    entry = SchemeTracking(**entry_dict)
    db.add(entry)
    await db.commit()

    # Re-fetch with loaded relationship
    stmt_reload = select(SchemeTracking).where(SchemeTracking.id == entry.id).options(selectinload(SchemeTracking.scheme))
    reloaded = (await db.execute(stmt_reload)).scalar_one()
    return SchemeTrackingResponse.model_validate(reloaded)


@router.put("/{tracking_id}", response_model=SchemeTrackingResponse, summary="Update Tracking Status / Notes")
@router.patch("/{tracking_id}", response_model=SchemeTrackingResponse, summary="Patch Tracking Status / Notes")
async def update_tracking(
    tracking_id: str,
    payload: SchemeTrackingUpdate,
    user_id: Optional[str] = Query(None, description="Optional user ID for isolation verification"),
    db: AsyncSession = Depends(get_db),
) -> SchemeTrackingResponse:
    stmt = select(SchemeTracking).where(SchemeTracking.id == tracking_id).options(selectinload(SchemeTracking.scheme))
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Tracking entry not found")

    if user_id and entry.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this application record")

    if payload.status:
        if payload.status not in VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status '{payload.status}'. Must be one of: {', '.join(VALID_STATUSES)}",
            )
        entry.status = payload.status
        if payload.status in ("Applied", "Application Submitted") and not entry.applied_at:
            from backend.app.database.models import utcnow
            entry.applied_at = utcnow()

    if payload.notes is not None:
        entry.notes = payload.notes

    await db.commit()
    await db.refresh(entry)
    return SchemeTrackingResponse.model_validate(entry)


@router.delete("/{tracking_id}", summary="Delete Application Tracking Entry")
async def delete_tracking(
    tracking_id: str,
    user_id: Optional[str] = Query(None, description="Optional user ID for isolation verification"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if user_id:
        stmt = delete(SchemeTracking).where(SchemeTracking.id == tracking_id, SchemeTracking.user_id == user_id)
    else:
        stmt = delete(SchemeTracking).where(SchemeTracking.id == tracking_id)

    result = await db.execute(stmt)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Application record not found or unauthorized")
    return {"message": "Tracking entry removed", "deleted": True}
