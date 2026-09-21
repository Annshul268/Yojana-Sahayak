"""CLI tool to build or refresh ChromaDB dense vector index for schemes."""

import argparse
import asyncio
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.core.logging import logger
from backend.app.database.connection import AsyncSessionLocal, init_db
from backend.app.database.models import Scheme
from backend.app.ingestion.pipeline import IngestionPipeline
from backend.app.rag.chroma import chroma_manager
from sqlalchemy import select


async def reindex_all() -> int:
    print(f"=======================================================")
    print(f"Indexing Schemes into ChromaDB Vector Store")
    print(f"=======================================================")
    
    await init_db()
    
    async with AsyncSessionLocal() as db:
        stmt = select(Scheme).where(Scheme.active == True)
        res = await db.execute(stmt)
        schemes = list(res.scalars().all())
        
    print(f"Found {len(schemes)} active schemes in database to index...")
    
    indexed = 0
    errors = 0
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
        try:
            chroma_manager.upsert_scheme_document(
                scheme_id=s.id,
                document_text=doc_text,
                metadata=metadata,
            )
            indexed += 1
        except Exception as exc:
            errors += 1
            print(f"  [ERROR] Failed to index '{s.slug}': {exc}")
            
    total_count = chroma_manager.count()
    print("\nChromaDB Indexing Summary:")
    print(f"- Total Schemes Processed: {len(schemes)}")
    print(f"- Successfully Indexed: {indexed}")
    print(f"- Failed: {errors}")
    print(f"- Current ChromaDB Collection Count: {total_count}")
    
    # Test query
    test_query = "scholarship for college students in Uttar Pradesh"
    print(f"\nTesting vector retrieval for: '{test_query}'...")
    results = chroma_manager.query(query_text=test_query, n_results=3)
    for r in results:
        meta = r.get("metadata", {})
        print(f"  - [{meta.get('slug')}] {meta.get('category')} (distance: {r.get('distance'):.4f})")
        
    return 0 if errors == 0 else 1


def main():
    parser = argparse.ArgumentParser(description="Index all active schemes into ChromaDB")
    args = parser.parse_args()
    exit_code = asyncio.run(reindex_all())
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
