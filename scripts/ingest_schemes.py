"""CLI tool to ingest government schemes into database and ChromaDB vector store."""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.core.logging import logger
from backend.app.database.connection import AsyncSessionLocal, init_db
from backend.app.database.models import Scheme
from backend.app.ingestion.pipeline import IngestionPipeline
from backend.app.ingestion.sources.curated import CuratedSource
from backend.app.rag.chroma import chroma_manager
from sqlalchemy import func, select


async def run_ingestion(file_path: Optional[str] = None, reindex: bool = True) -> int:
    source_file = file_path or "data/processed/schemes.json"
    if not Path(source_file).exists():
        source_file = "data/seed/schemes.json"
        
    print(f"=======================================================")
    print(f"Starting Scheme Ingestion from: {source_file}")
    print(f"=======================================================")
    
    # Initialize DB tables
    await init_db()
    
    source = CuratedSource(file_path=source_file)
    pipeline = IngestionPipeline(source=source)
    
    async with AsyncSessionLocal() as db:
        result = await pipeline.run(db)
        
        # Query current counts
        count_stmt = select(func.count(Scheme.id))
        res = await db.execute(count_stmt)
        total_db = res.scalar() or 0
        
    chroma_count = chroma_manager.count()
    
    print("\nIngestion Summary:")
    print(f"- Source: {result.get('source')}")
    print(f"- Total Fetched: {result.get('total_fetched')}")
    print(f"- Ingested/Updated: {result.get('ingested')}")
    print(f"- Failed: {result.get('failed')}")
    print(f"- Status: {result.get('status')}")
    print(f"- Total Schemes in DB: {total_db}")
    print(f"- Total Indexed in ChromaDB: {chroma_count}")
    
    if result.get("errors"):
        print("\nErrors encountered:")
        for err in result["errors"]:
            print(f"  - {err}")
        return 1
        
    print("\nScheme ingestion completed successfully!")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Ingest government schemes into database & ChromaDB")
    parser.add_argument("--file", type=str, default=None, help="Path to schemes JSON file")
    parser.add_argument("--no-reindex", action="store_true", help="Skip ChromaDB re-indexing")
    args = parser.parse_args()
    
    exit_code = asyncio.run(run_ingestion(file_path=args.file, reindex=not args.no_reindex))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
