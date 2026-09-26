"""Unit tests for Groq AI provider and assistant service."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.app.ai.groq_provider import GroqProvider
from backend.app.ai.service import AIService
from backend.app.core.config import settings


def test_groq_provider_default_model():
    """Verify GroqProvider defaults to openai/gpt-oss-120b from settings."""
    provider = GroqProvider()
    assert provider.model_name == "openai/gpt-oss-120b"


def test_groq_provider_custom_model():
    """Verify GroqProvider accepts an explicit model override."""
    provider = GroqProvider(model_name="custom-model")
    assert provider.model_name == "custom-model"


@pytest.mark.asyncio
async def test_groq_provider_error_handling():
    """Verify friendly error message on API failure without leaking stack trace or keys."""
    provider = GroqProvider()
    provider.client = MagicMock()
    provider.api_key = "test_key"
    provider.client.chat.completions.create = AsyncMock(side_effect=Exception("Internal upstream timeout"))

    messages = [{"role": "user", "content": "Hello"}]
    response = await provider.generate_response(messages)
    assert response == "AI Assistant is temporarily unavailable. Please try again."
    assert "Internal upstream timeout" not in response
    assert "test_key" not in response


@pytest.mark.asyncio
async def test_groq_provider_unconfigured_fallback():
    """Verify grounded fallback response when Groq provider is unconfigured."""
    provider = GroqProvider()
    provider.client = None
    provider.api_key = None

    messages = [{"role": "user", "content": "What documents do I need?"}]
    response = await provider.generate_response(messages)
    assert "Verified Government Information" in response
    assert "GROQ_API_KEY" in response


@pytest.mark.asyncio
async def test_ai_service_answer_question_with_mock_provider():
    """Verify AIService coordinates retrieval and provider response."""
    mock_provider = MagicMock()
    mock_provider.generate_response = AsyncMock(return_value="Applicants need Aadhaar and Bank Passbook.")
    mock_retriever = MagicMock()
    mock_retriever.retrieve_relevant_schemes.return_value = [
        {
            "scheme_id": "pm-kisan",
            "document": "PM Kisan Samman Nidhi provides financial benefit...",
            "metadata": {"category": "Agriculture", "official_url": "https://pmkisan.gov.in"},
        }
    ]

    service = AIService(provider=mock_provider, retriever=mock_retriever)
    result = await service.answer_question(question="What documents do I need?", language="en")

    assert result["question"] == "What documents do I need?"
    assert result["answer"] == "Applicants need Aadhaar and Bank Passbook."
    assert len(result["grounded_references"]) == 1
    assert result["grounded_references"][0]["scheme_id"] == "pm-kisan"
