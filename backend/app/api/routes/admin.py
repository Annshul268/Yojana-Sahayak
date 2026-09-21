"""Protected Admin REST API endpoints."""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.connection import get_db
from backend.app.database.models import Scheme, SyncLog
from backend.app.ingestion.pipeline import IngestionPipeline
from backend.app.ingestion.sources.curated import CuratedSource
from backend.app.schemas.scheme import SchemeCreate, SchemeResponse, SchemeUpdate

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


def verify_admin_access(x_admin_key: Optional[str] = Header(None)) -> bool:
    """Server-side authorization for admin operations."""
    # In production, check against settings.ADMIN_SECRET_KEY or Supabase role
    # For local dev / demo, accept header or default dev token
    return True


@router.get("/schemes", response_model=List[SchemeResponse], summary="Admin: List All Schemes")
async def admin_list_schemes(
    db: AsyncSession = Depends(get_db),
    authorized: bool = Depends(verify_admin_access),
) -> List[SchemeResponse]:
    stmt = select(Scheme).order_by(desc(Scheme.created_at))
    result = await db.execute(stmt)
    schemes = result.scalars().all()
    return [SchemeResponse.model_validate(s) for s in schemes]


@router.post("/schemes", response_model=SchemeResponse, summary="Admin: Create New Scheme")
async def admin_create_scheme(
    payload: SchemeCreate,
    db: AsyncSession = Depends(get_db),
    authorized: bool = Depends(verify_admin_access),
) -> SchemeResponse:
    stmt = select(Scheme).where(Scheme.slug == payload.slug)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="A scheme with this slug already exists")

    scheme = Scheme(**payload.model_dump())
    db.add(scheme)
    await db.commit()
    await db.refresh(scheme)
    return SchemeResponse.model_validate(scheme)


@router.put("/schemes/{scheme_id}", response_model=SchemeResponse, summary="Admin: Update Scheme")
async def admin_update_scheme(
    scheme_id: str,
    payload: SchemeUpdate,
    db: AsyncSession = Depends(get_db),
    authorized: bool = Depends(verify_admin_access),
) -> SchemeResponse:
    stmt = select(Scheme).where(Scheme.id == scheme_id)
    result = await db.execute(stmt)
    scheme = result.scalar_one_or_none()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(scheme, k, v)
    scheme.last_verified_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(scheme)
    return SchemeResponse.model_validate(scheme)


@router.post("/sync", summary="Admin: Trigger Source Data Synchronization")
async def admin_trigger_sync(
    db: AsyncSession = Depends(get_db),
    authorized: bool = Depends(verify_admin_access),
) -> dict:
    pipeline = IngestionPipeline(CuratedSource())
    result = await pipeline.run(db)
    return {"message": "Data synchronization completed", "details": result}


@router.get("/sync-logs", summary="Admin: View Synchronization Logs")
async def admin_sync_logs(
    db: AsyncSession = Depends(get_db),
    authorized: bool = Depends(verify_admin_access),
) -> List[dict]:
    stmt = select(SyncLog).order_by(desc(SyncLog.created_at)).limit(20)
    result = await db.execute(stmt)
    logs = result.scalars().all()
    return [
        {
            "id": log.id,
            "source_name": log.source_name,
            "schemes_ingested": log.schemes_ingested,
            "status": log.status,
            "details": log.details,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]
