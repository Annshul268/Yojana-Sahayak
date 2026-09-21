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


@router.get("/intents", summary="List Available Top-Level Intent Taxonomy")
async def list_intents():
    """Returns top-level intent categories and candidate tags for dynamic questionnaires."""
    from backend.app.matching.taxonomy import get_all_intents
    return get_all_intents()
