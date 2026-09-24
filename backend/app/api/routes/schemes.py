"""Schemes REST API endpoints."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select, String
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.connection import get_db
from backend.app.database.models import Scheme
from backend.app.schemas.scheme import SchemeListResponse, SchemeResponse

router = APIRouter(prefix="/schemes", tags=["Schemes"])

CATEGORY_ICONS = {
    "Education & Learning": "🎓",
    "Social Security & Pension": "👴",
    "Women & Child Development": "👩‍👧",
    "Agriculture & Rural Development": "🌾",
    "Business & Self Employment": "💼",
    "Healthcare": "🏥",
    "Employment & Skills": "🛠️",
    "Housing & Shelter": "🏠",
    "Differently Abled Support": "♿",
    "Financial Assistance": "💳",
    "Social Welfare": "🤝",
}

CATEGORY_HI = {
    "Education & Learning": "शिक्षा एवं छात्रवृत्ति",
    "Social Security & Pension": "सामाजिक सुरक्षा एवं पेंशन",
    "Women & Child Development": "महिला एवं बाल विकास",
    "Agriculture & Rural Development": "कृषि एवं ग्रामीण विकास",
    "Business & Self Employment": "व्यवसाय एवं स्वरोजगार",
    "Healthcare": "स्वास्थ्य एवं चिकित्सा",
    "Employment & Skills": "रोजगार एवं कौशल",
    "Housing & Shelter": "आवास एवं आश्रय",
    "Differently Abled Support": "दिव्यांगजन सहायता",
    "Financial Assistance": "वित्तीय सहायता",
    "Social Welfare": "समाज कल्याण",
}

DEFAULT_FEATURED_SLUGS = [
    "up-post-matric-scholarship-obc",
    "pmay-gramin",
    "adip-scheme-disabled",
    "ayushman-bharat-pmjay",
    "pm-kisan",
]


@router.get("/featured", response_model=List[SchemeResponse], summary="Featured Government Schemes for Carousel")
async def get_featured_schemes(
    limit: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
) -> List[SchemeResponse]:
    """Retrieve verified featured schemes for the home page carousel."""
    # First attempt: schemes with is_featured=True ordered by priority
    stmt = (
        select(Scheme)
        .where(Scheme.active == True, Scheme.is_featured == True)
        .order_by(Scheme.featured_priority.desc(), Scheme.name.asc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    featured = list(result.scalars().all())

    # Fallback if fewer than required featured schemes exist
    if len(featured) < limit:
        existing_ids = {s.id for s in featured}
        fallback_stmt = (
            select(Scheme)
            .where(Scheme.active == True, Scheme.slug.in_(DEFAULT_FEATURED_SLUGS))
            .order_by(Scheme.level.asc(), Scheme.name.asc())
        )
        res_fb = await db.execute(fallback_stmt)
        for s in res_fb.scalars().all():
            if s.id not in existing_ids and len(featured) < limit:
                featured.append(s)
                existing_ids.add(s.id)

    # Secondary fallback if still under limit
    if len(featured) < limit:
        existing_ids = {s.id for s in featured}
        more_stmt = (
            select(Scheme)
            .where(Scheme.active == True)
            .order_by(Scheme.level.asc(), Scheme.name.asc())
            .limit(limit * 2)
        )
        res_more = await db.execute(more_stmt)
        for s in res_more.scalars().all():
            if s.id not in existing_ids and len(featured) < limit:
                featured.append(s)
                existing_ids.add(s.id)

    return [SchemeResponse.model_validate(s) for s in featured]


@router.get("/stats", summary="Actual Database Scheme Statistics")
@router.get("/statistics", summary="Actual Database Scheme Statistics")
async def get_scheme_stats(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Calculate aggregated scheme metrics dynamically from PostgreSQL / SQLite."""
    stmt = select(Scheme).where(Scheme.active == True)
    result = await db.execute(stmt)
    all_schemes = list(result.scalars().all())

    total = len(all_schemes)
    central = 0
    state_count = 0
    category_counts: Dict[str, int] = {}
    state_counts: Dict[str, int] = {}

    for s in all_schemes:
        if (s.level or "").capitalize() == "Central" or (s.states and "ALL" in [str(x).upper() for x in s.states]):
            central += 1
        else:
            state_count += 1

        cat = s.category or "Other"
        category_counts[cat] = category_counts.get(cat, 0) + 1

        for st in (s.states or []):
            st_clean = str(st).strip()
            if st_clean.upper() != "ALL":
                state_counts[st_clean] = state_counts.get(st_clean, 0) + 1

    # Sorted state and category statistics
    sorted_categories = dict(sorted(category_counts.items(), key=lambda item: item[1], reverse=True))
    sorted_states = dict(sorted(state_counts.items(), key=lambda item: item[1], reverse=True))

    return {
        "total": total,
        "central": central,
        "state": state_count,
        "categories": sorted_categories,
        "states": sorted_states,
    }


@router.get("/categories", summary="List Categories with Dynamic Counts")
async def get_scheme_categories(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """List all categories with actual counts, icons, and bilingual labels."""
    stmt = select(Scheme.category, func.count(Scheme.id)).where(Scheme.active == True).group_by(Scheme.category)
    result = await db.execute(stmt)
    rows = result.all()

    cats = []
    for cat_name, count in sorted(rows, key=lambda r: r[1], reverse=True):
        cats.append({
            "name": cat_name,
            "name_hi": CATEGORY_HI.get(cat_name, cat_name),
            "count": count,
            "icon": CATEGORY_ICONS.get(cat_name, "📋"),
        })
    return cats


@router.get("/states", summary="List States with Dynamic Counts")
async def get_scheme_states(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """List all states with state-specific and total applicable scheme counts."""
    stmt = select(Scheme).where(Scheme.active == True)
    result = await db.execute(stmt)
    schemes = list(result.scalars().all())

    central_count = sum(1 for s in schemes if (s.level or "").capitalize() == "Central")
    state_map: Dict[str, int] = {}

    for s in schemes:
        for st in (s.states or []):
            st_name = str(st).strip()
            if st_name.upper() != "ALL":
                state_map[st_name] = state_map.get(st_name, 0) + 1

    result_list = []
    for state_name, count in sorted(state_map.items(), key=lambda x: x[1], reverse=True):
        result_list.append({
            "state": state_name,
            "state_count": count,
            "central_count": central_count,
            "total_applicable": count + central_count,
        })
    return result_list


@router.get("", response_model=SchemeListResponse, summary="Browse & Search Schemes")
async def list_schemes(
    q: Optional[str] = Query(None, description="Keyword search in title, description, or category"),
    category: Optional[str] = Query(None, description="Filter by scheme category"),
    ministry: Optional[str] = Query(None, description="Filter by ministry"),
    state: Optional[str] = Query(None, description="Filter by state name"),
    level: Optional[str] = Query(None, description="Filter by level ('Central' or 'State')"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
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

    if category and category.upper() != "ALL":
        query = query.where(Scheme.category == category)
    if ministry and ministry.upper() != "ALL":
        query = query.where(Scheme.ministry == ministry)
    if level and level.upper() != "ALL":
        query = query.where(Scheme.level == level)

    # Proper state filtering: Central schemes + State's specific schemes
    if state and state.upper() != "ALL":
        state_clean = state.strip()
        state_cond = or_(
            Scheme.level == "Central",
            Scheme.states.cast(String).ilike('%"ALL"%'),
            Scheme.states.cast(String).ilike(f'%"%{state_clean}%"%'),
            Scheme.states.cast(String).ilike(f'%{state_clean}%'),
        )
        query = query.where(state_cond)

    # Count total matching schemes
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.order_by(Scheme.name.asc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    schemes = result.scalars().all()

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
