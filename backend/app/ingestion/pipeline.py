"""Government scheme data ingestion pipeline orchestrator."""

from datetime import datetime, timezone
from typing import Any, Dict, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.logging import logger
from backend.app.database.models import Scheme, SyncLog
from backend.app.ingestion.cleaner import SchemeCleaner
from backend.app.ingestion.sources.base import SchemeSource
from backend.app.ingestion.validator import SchemeValidator
from backend.app.rag.chroma import chroma_manager


class IngestionPipeline:
    """Orchestrates: Source -> Clean -> Validate -> DB Storage -> Vector Embeddings."""

    def __init__(self, source: SchemeSource):
        self.source = source
        self.cleaner = SchemeCleaner()
        self.validator = SchemeValidator()

    @staticmethod
    def build_embedding_text(scheme_dict: Dict[str, Any]) -> str:
        """Constructs a comprehensive document text block for dense vector embedding."""
        parts = [
            f"Scheme Name: {scheme_dict.get('name')}",
            f"Hindi Name: {scheme_dict.get('name_hi', '')}",
            f"Category: {scheme_dict.get('category')}",
            f"Ministry: {scheme_dict.get('ministry')}",
            f"Description: {scheme_dict.get('description')}",
            f"Hindi Description: {scheme_dict.get('description_hi', '')}",
            f"Benefits: {'; '.join(scheme_dict.get('benefits', []))}",
            f"Documents Required: {'; '.join(scheme_dict.get('documents', []))}",
            f"Application Procedure: {'; '.join(scheme_dict.get('application_steps', []))}",
        ]
        return "\n".join(parts)

    async def run(self, db: AsyncSession) -> Dict[str, Any]:
        source_name = self.source.get_source_name()
        logger.info("Starting ingestion pipeline for: %s", source_name)
        raw_items = await self.source.fetch_schemes()
        total_fetched = len(raw_items)
        ingested_count = 0
        failed_count = 0
        error_details: List[str] = []

        chroma_already_indexed = False
        try:
            chroma_already_indexed = chroma_manager.collection.count() >= total_fetched
            if chroma_already_indexed:
                logger.info(
                    "ChromaDB collection already contains %d documents. Skipping re-embedding.",
                    chroma_manager.collection.count(),
                )
        except Exception:
            chroma_already_indexed = False

        for raw_item in raw_items:
            cleaned = self.cleaner.clean(raw_item)
            is_valid, errors = self.validator.validate(cleaned)
            if not is_valid:
                failed_count += 1
                error_details.append(f"Scheme '{cleaned.get('slug')}': {', '.join(errors)}")
                continue

            slug = cleaned["slug"]
            stmt = select(Scheme).where(Scheme.slug == slug)
            res = await db.execute(stmt)
            existing_scheme = res.scalar_one_or_none()

            valid_columns = {c.name for c in Scheme.__table__.columns}
            filtered_data = {k: v for k, v in cleaned.items() if k in valid_columns}

            if existing_scheme:
                # Update existing record
                for k, v in filtered_data.items():
                    if hasattr(existing_scheme, k):
                        setattr(existing_scheme, k, v)
                existing_scheme.last_verified_at = datetime.now(timezone.utc)
                scheme_id = existing_scheme.id
            else:
                new_scheme = Scheme(**filtered_data)
                db.add(new_scheme)
                await db.flush()
                scheme_id = new_scheme.id

            # Create & index in ChromaDB only if not already indexed
            if not chroma_already_indexed:
                doc_text = self.build_embedding_text(cleaned)
                metadata = {
                    "scheme_id": scheme_id,
                    "slug": slug,
                    "category": cleaned.get("category", ""),
                    "ministry": cleaned.get("ministry", ""),
                    "level": cleaned.get("level", "Central"),
                    "source": source_name,
                    "official_url": cleaned.get("official_url", ""),
                }
                try:
                    chroma_manager.upsert_scheme_document(
                        scheme_id=scheme_id,
                        document_text=doc_text,
                        metadata=metadata,
                    )
                except Exception as exc:
                    logger.error("Failed to index scheme '%s' in ChromaDB: %s", slug, exc)

            ingested_count += 1

        # Record synchronization log in database
        status = "Success" if failed_count == 0 else ("Partial" if ingested_count > 0 else "Failed")
        sync_log = SyncLog(
            source_name=source_name,
            schemes_ingested=ingested_count,
            status=status,
            details=f"Fetched: {total_fetched}, Ingested: {ingested_count}, Errors: {len(error_details)}",
        )
        db.add(sync_log)
        await db.commit()

        logger.info(
            "Ingestion completed for %s. Ingested: %d, Failed: %d",
            source_name,
            ingested_count,
            failed_count,
        )
        return {
            "source": source_name,
            "total_fetched": total_fetched,
            "ingested": ingested_count,
            "failed": failed_count,
            "status": status,
            "errors": error_details,
        }
