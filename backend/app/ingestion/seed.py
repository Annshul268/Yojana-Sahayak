"""Seed helper to initialize schemes on application startup."""

from sqlalchemy import func, select
from backend.app.core.logging import logger
from backend.app.database.connection import AsyncSessionLocal
from backend.app.database.models import Scheme
from backend.app.ingestion.sources.curated import CuratedSource


async def seed_database_if_empty() -> None:
    """Seeds the database with curated schemes if no schemes exist."""
    async with AsyncSessionLocal() as db:
        try:
            count_stmt = select(func.count(Scheme.id))
            result = await db.execute(count_stmt)
            count = result.scalar() or 0
            if count == 0:
                logger.info("Database schemes table is empty. Running fast initial curated seed...")
                source = CuratedSource()
                raw_items = await source.fetch_schemes()
                if not raw_items:
                    logger.warning("No seed schemes found to populate database.")
                    return

                from backend.app.ingestion.cleaner import SchemeCleaner
                from backend.app.ingestion.validator import SchemeValidator

                cleaner = SchemeCleaner()
                validator = SchemeValidator()
                valid_columns = {c.name for c in Scheme.__table__.columns}

                schemes_to_insert = []
                for item in raw_items:
                    cleaned = cleaner.clean(item)
                    is_valid, _ = validator.validate(cleaned)
                    if is_valid:
                        filtered = {k: v for k, v in cleaned.items() if k in valid_columns}
                        schemes_to_insert.append(Scheme(**filtered))

                db.add_all(schemes_to_insert)
                await db.commit()
                logger.info("Initial seed completed: %d schemes inserted into database.", len(schemes_to_insert))
            else:
                logger.info("Database already contains %d schemes. Skipping seed.", count)
        except Exception as exc:
            logger.error("Error during auto-seed: %s", exc)
