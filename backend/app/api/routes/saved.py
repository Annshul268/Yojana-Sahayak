"""Saved Schemes REST API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.app.database.connection import get_db
from backend.app.database.models import SavedScheme, Scheme
from backend.app.schemas.tracking import SavedSchemeResponse

router = APIRouter(prefix="/saved", tags=["Saved Schemes"])


@router.get("", response_model=List[SavedSchemeResponse], summary="List Citizen Saved Schemes")
async def list_saved_schemes(
    user_id: str = Query(..., description="Unique citizen identifier"),
    db: AsyncSession = Depends(get_db),
) -> List[SavedSchemeResponse]:
    stmt = (
        select(SavedScheme)
        .where(SavedScheme.user_id == user_id)
        .options(selectinload(SavedScheme.scheme))
        .order_by(SavedScheme.created_at.desc())
    )
    result = await db.execute(stmt)
    saved = result.scalars().all()
    return [SavedSchemeResponse.model_validate(s) for s in saved]


@router.post("/{scheme_id}", response_model=SavedSchemeResponse, summary="Save/Bookmark a Scheme")
async def save_scheme(
    scheme_id: str,
    user_id: str = Query(..., description="Unique citizen identifier"),
    db: AsyncSession = Depends(get_db),
) -> SavedSchemeResponse:
    # Check scheme exists
    scheme_stmt = select(Scheme).where(Scheme.id == scheme_id)
    s_res = await db.execute(scheme_stmt)
    scheme = s_res.scalar_one_or_none()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    # Check if already saved
    stmt = select(SavedScheme).where(
        SavedScheme.user_id == user_id,
        SavedScheme.scheme_id == scheme_id,
    ).options(selectinload(SavedScheme.scheme))
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        return SavedSchemeResponse.model_validate(existing)

    new_saved = SavedScheme(user_id=user_id, scheme_id=scheme_id)
    db.add(new_saved)
    await db.commit()

    # Re-fetch with loaded relationship
    stmt_reload = select(SavedScheme).where(SavedScheme.id == new_saved.id).options(selectinload(SavedScheme.scheme))
    reloaded = (await db.execute(stmt_reload)).scalar_one()
    return SavedSchemeResponse.model_validate(reloaded)


@router.delete("/{scheme_id}", summary="Remove Saved Scheme")
async def remove_saved_scheme(
    scheme_id: str,
    user_id: str = Query(..., description="Unique citizen identifier"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    stmt = delete(SavedScheme).where(
        SavedScheme.user_id == user_id,
        SavedScheme.scheme_id == scheme_id,
    )
    result = await db.execute(stmt)
    await db.commit()
    return {"message": "Scheme removed from bookmarks", "deleted": result.rowcount > 0}
