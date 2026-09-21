"""Deterministic matching API route."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.connection import get_db
from backend.app.database.models import Scheme
from backend.app.matching.engine import matching_engine
from backend.app.matching.models import CitizenProfileInput, MatchResponse

router = APIRouter(prefix="/schemes", tags=["Matching Engine"])


@router.post("/match", response_model=MatchResponse, summary="Match Citizen Against All Government Schemes")
async def match_citizen_schemes(
    profile: CitizenProfileInput,
    db: AsyncSession = Depends(get_db),
) -> MatchResponse:
    """Evaluates the citizen profile deterministically against all active government schemes."""
    stmt = select(Scheme).where(Scheme.active == True)
    result = await db.execute(stmt)
    schemes = list(result.scalars().all())

    return matching_engine.match_all(schemes=schemes, profile=profile)
