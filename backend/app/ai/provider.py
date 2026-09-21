"""Abstract base class for AI Provider."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AIProvider(ABC):
    """Interface for AI LLM providers."""

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the provider is configured and available."""
        pass

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 800,
    ) -> str:
        """Generates a text completion given message conversation history."""
        pass
