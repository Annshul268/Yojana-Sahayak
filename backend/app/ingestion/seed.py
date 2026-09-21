"""Seed helper to initialize schemes on application startup."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.logging import logger
from backend.app.database.connection import AsyncSessionLocal
from backend.app.database.models import Scheme
from backend.app.ingestion.pipeline import IngestionPipeline
from backend.app.ingestion.sources.curated import CuratedSource


async def seed_database_if_empty() -> None:
    """Seeds the database with curated schemes if no schemes exist."""
    async with AsyncSessionLocal() as db:
        try:
            count_stmt = select(func.count(Scheme.id))
            result = await db.execute(count_stmt)
            count = result.scalar() or 0
            if count == 0:
                logger.info("Database schemes table is empty. Running initial curated seed...")
                pipeline = IngestionPipeline(CuratedSource())
                res = await pipeline.run(db)
                logger.info("Initial seed completed: %s", res)
            else:
                logger.info("Database already contains %d schemes. Skipping auto-seed.", count)
        except Exception as exc:
            logger.error("Error during auto-seed: %s", exc)
