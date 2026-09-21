"""Base abstract class for government scheme sources."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class SchemeSource(ABC):
    """Abstract interface for external and curated government scheme sources."""

    @abstractmethod
    def get_source_name(self) -> str:
        """Returns the canonical name of the source."""
        pass

    @abstractmethod
    async def fetch_schemes(self) -> List[Dict[str, Any]]:
        """Fetches raw scheme records from the source."""
        pass
