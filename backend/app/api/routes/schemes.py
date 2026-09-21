"""Schemes REST API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.connection import get_db
from backend.app.database.models import Scheme
from backend.app.schemas.scheme import SchemeListResponse, SchemeResponse

router = APIRouter(prefix="/schemes", tags=["Schemes"])


@router.get("", response_model=SchemeListResponse, summary="Browse & Search Schemes")
async def list_schemes(
    q: Optional[str] = Query(None, description="Keyword search in title, description, or category"),
    category: Optional[str] = Query(None, description="Filter by scheme category"),
    ministry: Optional[str] = Query(None, description="Filter by ministry"),
    state: Optional[str] = Query(None, description="Filter by state name"),
    level: Optional[str] = Query(None, description="Filter by level ('Central' or 'State')"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> SchemeListResponse:
    query = select(Scheme).where(Scheme.active == True)

    if q:
        search_pattern = f"%{q.strip()}%"
        query = query.where(
            or_(
                Scheme.name.ilike(search_pattern),
                Scheme.name_hi.ilike(search_pattern),
                Scheme.description.ilike(search_pattern),
                Scheme.description_hi.ilike(search_pattern),
                Scheme.category.ilike(search_pattern),
                Scheme.ministry.ilike(search_pattern),
            )
        )

    if category:
        query = query.where(Scheme.category == category)
    if ministry:
        query = query.where(Scheme.ministry == ministry)
    if level:
        query = query.where(Scheme.level == level)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.order_by(Scheme.name.asc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    schemes = result.scalars().all()

    # Filter state in python if state provided (checking JSON array)
    if state and state.upper() != "ALL":
        filtered = []
        for s in schemes:
            st_list = [x.upper() for x in (s.states or [])]
            if "ALL" in st_list or state.upper() in st_list:
                filtered.append(s)
        schemes = filtered

    return SchemeListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[SchemeResponse.model_validate(s) for s in schemes],
    )


@router.get("/{slug_or_id}", response_model=SchemeResponse, summary="Get Scheme by Slug or ID")
async def get_scheme(slug_or_id: str, db: AsyncSession = Depends(get_db)) -> SchemeResponse:
    query = select(Scheme).where(
        or_(Scheme.slug == slug_or_id, Scheme.id == slug_or_id)
    )
    result = await db.execute(query)
    scheme = result.scalar_one_or_none()
    if not scheme:
        raise HTTPException(status_code=404, detail="Government scheme not found")
    return SchemeResponse.model_validate(scheme)
