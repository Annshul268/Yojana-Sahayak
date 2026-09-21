"""Curated government schemes source reader."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from backend.app.core.logging import logger
from backend.app.ingestion.sources.base import SchemeSource


class CuratedSource(SchemeSource):
    """Loads curated and verified government welfare schemes from local storage."""

    def __init__(self, file_path: Optional[str] = None):
        if file_path:
            self.file_path = Path(file_path)
        else:
            processed = Path("data/processed/schemes.json")
            self.file_path = processed if processed.exists() else Path("data/seed/schemes.json")

    def get_source_name(self) -> str:
        return "Curated Government Schemes"

    async def fetch_schemes(self) -> List[Dict[str, Any]]:
        if not self.file_path.exists():
            logger.warning("Curated scheme file not found at: %s", self.file_path)
            return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info("Loaded %d curated schemes from %s", len(data), self.file_path)
            return data
