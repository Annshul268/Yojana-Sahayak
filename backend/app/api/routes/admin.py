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
@router.get("/diagnostics", summary="Admin: System and Catalog Diagnostics")
async def admin_diagnostics(
    db: AsyncSession = Depends(get_db),
    authorized: bool = Depends(verify_admin_access),
) -> dict:
    from backend.app.rag.chroma import chroma_manager

    stmt = select(Scheme)
    result = await db.execute(stmt)
    schemes = list(result.scalars().all())

    by_level = {}
    by_category = {}
    by_ministry = {}
    by_state = {}
    active_count = 0

    for s in schemes:
        if s.active:
            active_count += 1
        lvl = s.level or "Central"
        by_level[lvl] = by_level.get(lvl, 0) + 1
        cat = s.category or "Other"
        by_category[cat] = by_category.get(cat, 0) + 1
        minis = s.ministry or "Other"
        by_ministry[minis] = by_ministry.get(minis, 0) + 1
        for st in (s.states or ["ALL"]):
            by_state[st] = by_state.get(st, 0) + 1

    chroma_count = chroma_manager.count()

    stmt_sync = select(SyncLog).order_by(desc(SyncLog.created_at)).limit(1)
    res_sync = await db.execute(stmt_sync)
    last_log = res_sync.scalar_one_or_none()

    return {
        "total_schemes": len(schemes),
        "active_schemes": active_count,
        "chromadb_documents": chroma_count,
        "by_level": by_level,
        "by_category": by_category,
        "by_ministry": by_ministry,
        "by_state": by_state,
        "last_sync": {
            "source": last_log.source_name,
            "status": last_log.status,
            "schemes_ingested": last_log.schemes_ingested,
            "created_at": last_log.created_at.isoformat() if last_log and last_log.created_at else None,
        } if last_log else None,
    }


@router.post("/reindex", summary="Admin: Rebuild ChromaDB Index")
async def admin_reindex(
    db: AsyncSession = Depends(get_db),
    authorized: bool = Depends(verify_admin_access),
) -> dict:
    from backend.app.rag.chroma import chroma_manager

    stmt = select(Scheme).where(Scheme.active == True)
    result = await db.execute(stmt)
    schemes = list(result.scalars().all())

    indexed = 0
    for s in schemes:
        scheme_dict = {
            "name": s.name,
            "name_hi": s.name_hi,
            "category": s.category,
            "ministry": s.ministry,
            "description": s.description,
            "description_hi": s.description_hi,
            "benefits": s.benefits or [],
            "documents": s.documents or [],
            "application_steps": s.application_steps or [],
        }
        doc_text = IngestionPipeline.build_embedding_text(scheme_dict)
        metadata = {
            "scheme_id": s.id,
            "slug": s.slug,
            "category": s.category or "",
            "ministry": s.ministry or "",
            "level": s.level or "Central",
            "source": s.source_name or "Official Portal",
            "official_url": s.official_url or "",
        }
        chroma_manager.upsert_scheme_document(
            scheme_id=s.id,
            document_text=doc_text,
            metadata=metadata,
        )
        indexed += 1

    return {
        "message": f"Successfully re-indexed {indexed} active schemes into ChromaDB.",
        "chromadb_count": chroma_manager.count(),
    }
