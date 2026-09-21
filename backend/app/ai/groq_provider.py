"""Groq AI Provider implementation using Llama models."""

import os
from typing import Dict, List
from backend.app.ai.provider import AIProvider
from backend.app.core.config import settings
from backend.app.core.logging import logger

try:
    from groq import AsyncGroq
except ImportError:
    AsyncGroq = None  # type: ignore


class GroqProvider(AIProvider):
    """Integrates with Groq API running high-speed Llama models."""

    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        self.model_name = model_name
        self.client = None
        if self.api_key and AsyncGroq is not None:
            try:
                self.client = AsyncGroq(api_key=self.api_key)
                logger.info("GroqProvider initialized with model: %s", self.model_name)
            except Exception as exc:
                logger.warning("Failed to initialize Groq client: %s", exc)

    def is_available(self) -> bool:
        return bool(self.client is not None and self.api_key)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 800,
    ) -> str:
        if not self.is_available():
            logger.info("Groq API key not set; providing grounded fallback response.")
            # Extract last user message
            last_msg = messages[-1]["content"] if messages else ""
            return (
                "ℹ️ **Verified Government Information:**\n\n"
                "All scheme criteria, benefits, and application processes shown above are retrieved directly from official government databases. "
                "(To activate conversational AI explanations with Groq Llama, configure `GROQ_API_KEY` in your `.env` file.)"
            )

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.error("Groq API request failed: %s", exc)
            return (
                f"An error occurred while communicating with the AI service: {str(exc)}. "
                "Please refer to the verified scheme criteria listed above."
            )


groq_provider = GroqProvider()
