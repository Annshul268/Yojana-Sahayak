"""Tests for Featured Schemes Carousel Navigation and Grounded AI Explain functionality."""

import os
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from frontend.components.featured_carousel import render_featured_carousel
from frontend.services.api_client import APIClient, get_backend_api_url
from backend.app.ai.service import AIService
from backend.app.schemas.ai import AskAIRequest, ExplainEligibilityRequest


class TestFeaturedCarouselRenderingAndNavigation:
    """Verifies that the featured carousel renders proper Streamlit-compatible navigation."""

    @patch("streamlit.components.v1.html")
    def test_carousel_html_contains_open_scheme_navigation(self, mock_components_html):
        schemes = [
            {
                "slug": "pm-kisan",
                "name": "PM Kisan Samman Nidhi",
                "description": "Financial support to farmer families.",
                "category": "Agriculture",
                "level": "Central",
                "official_url": "https://pmkisan.gov.in",
            },
            {
                "slug": "ayushman-bharat-pmjay",
                "name": "Ayushman Bharat PM-JAY",
                "description": "Health coverage of 5 lakhs per family.",
                "category": "Healthcare",
                "level": "Central",
                "official_url": "https://pmjay.gov.in",
            },
            {
                "slug": "pmay-gramin",
                "name": "PMAY Gramin",
                "description": "Housing assistance for rural poor.",
                "category": "Housing & Shelter",
                "level": "Central",
                "official_url": "https://pmayg.nic.in",
            },
        ]

        render_featured_carousel(schemes, lang="en")
        assert mock_components_html.called
        html_code = mock_components_html.call_args[0][0]

        # 1. Ensure openScheme navigation function is present
        assert "function openScheme(slug, officialUrl)" in html_code
        assert "pUrl.searchParams.set(\"scheme\", slug)" in html_code
        assert "pWin.location.href = pUrl.toString()" in html_code

        # 2. Ensure card is div and banner is clickable
        assert "const card = document.createElement(\"div\")" in html_code
        assert "banner.setAttribute(\"role\", \"button\")" in html_code
        assert "openScheme(s.slug, s.official_url)" in html_code

        # 3. Ensure View button is a clickable button element
        assert "const btn = document.createElement(\"button\")" in html_code
        assert "btn.addEventListener(\"click\"" in html_code

        # 4. Ensure arrows stop propagation and only change slides
        assert "prevArrow.addEventListener(\"click\"" in html_code
        assert "e.stopPropagation()" in html_code
        assert "prevSlide()" in html_code
        assert "nextSlide()" in html_code

        # 5. Ensure all 3 schemes are included
        assert "pm-kisan" in html_code
        assert "ayushman-bharat-pmjay" in html_code
        assert "pmay-gramin" in html_code


class TestBackendURLResolution:
    """Verifies that the API client correctly resolves production backend URLs."""

    def test_get_backend_api_url_env_override(self):
        with patch.dict(os.environ, {"BACKEND_API_URL": "https://yojana-sahayak.onrender.com"}, clear=False):
            url = get_backend_api_url()
            assert url == "https://yojana-sahayak.onrender.com"

    def test_get_backend_api_url_api_base_url_env(self):
        with patch.dict(os.environ, {"BACKEND_API_URL": "", "API_BASE_URL": "https://backend.onrender.com"}, clear=False):
            # When BACKEND_API_URL is empty, API_BASE_URL is used
            url = get_backend_api_url()
            assert url == "https://backend.onrender.com"

    def test_api_client_dynamic_property(self):
        client = APIClient()
        with patch.dict(os.environ, {"BACKEND_API_URL": "https://custom-backend.render.com"}, clear=False):
            assert client.base_url == "https://custom-backend.render.com"


class TestGroundedAIExplainService:
    """Verifies grounded AI explanations and database fallback."""

    @pytest.mark.asyncio
    async def test_explain_eligibility_grounded_fallback_from_database(self):
        """When Groq is unavailable, explain_eligibility fetches verified data from DB."""
        mock_provider = MagicMock()
        mock_provider.is_available.return_value = False

        service = AIService(provider=mock_provider)

        # Mock database scheme lookup
        fake_scheme = {
            "id": "test-uuid-1",
            "slug": "pm-kisan",
            "name": "PM Kisan Samman Nidhi",
            "name_hi": "पीएम किसान सम्मान निधि",
            "description": "Income support scheme for farmers.",
            "description_hi": "किसानों के लिए आय सहायता योजना।",
            "category": "Agriculture",
            "ministry": "Ministry of Agriculture",
            "benefits": ["Rs 6,000 per year in 3 installments"],
            "documents": ["Aadhaar Card", "Land Ownership Documents", "Bank Passbook"],
            "eligibility_rules": {"landholding": "<= 2 hectares"},
            "application_steps": ["Register on PM-Kisan portal"],
            "official_url": "https://pmkisan.gov.in",
        }

        with patch.object(service, "_lookup_scheme", AsyncMock(return_value=fake_scheme)):
            explanation = await service.explain_eligibility(scheme_slug="pm-kisan", language="en")

            assert "PM Kisan Samman Nidhi" in explanation
            assert "Key Benefits" in explanation
            assert "Rs 6,000 per year" in explanation
            assert "Required Documents" in explanation
            assert "Aadhaar Card" in explanation
            assert "https://pmkisan.gov.in" in explanation

    @pytest.mark.asyncio
    async def test_answer_question_with_scheme_slug_grounds_in_verified_data(self):
        """Questions for a specific scheme incorporate verified DB facts as context."""
        mock_provider = MagicMock()
        mock_provider.is_available.return_value = True
        mock_provider.generate_response = AsyncMock(return_value="Applicants need Aadhaar and land records.")

        mock_retriever = MagicMock()
        mock_retriever.retrieve_relevant_schemes.return_value = []

        service = AIService(provider=mock_provider, retriever=mock_retriever)

        fake_scheme = {
            "id": "pm-kisan-id",
            "slug": "pm-kisan",
            "name": "PM Kisan",
            "name_hi": "पीएम किसान",
            "description": "Financial support",
            "description_hi": "वित्तीय सहायता",
            "category": "Agriculture",
            "ministry": "Agriculture Ministry",
            "benefits": ["Rs 6000"],
            "documents": ["Aadhaar", "Land Record"],
            "eligibility_rules": {},
            "application_steps": [],
            "official_url": "https://pmkisan.gov.in",
        }

        with patch.object(service, "_lookup_scheme", AsyncMock(return_value=fake_scheme)):
            res = await service.answer_question(
                question="What documents are needed?",
                language="en",
                scheme_slug="pm-kisan",
            )

            assert res["answer"] == "Applicants need Aadhaar and land records."
            assert len(res["grounded_references"]) == 1
            assert res["grounded_references"][0]["scheme_id"] == "pm-kisan-id"

            # Check that provider was called with verified scheme facts
            called_messages = mock_provider.generate_response.call_args[0][0]
            system_msg = next(m["content"] for m in called_messages if m["role"] == "system")
            assert "VERIFIED DATABASE RECORD FOR THIS SCHEME" in system_msg
            assert "PM Kisan" in system_msg
            assert "Aadhaar" in system_msg

    def test_schemas_accept_scheme_identifiers(self):
        """Verify request schemas correctly parse scheme_id and scheme_slug."""
        req1 = ExplainEligibilityRequest(scheme_slug="pm-kisan", language="en")
        assert req1.scheme_slug == "pm-kisan"
        assert req1.match_result is None

        req2 = AskAIRequest(question="How to apply?", scheme_slug="pm-kisan")
        assert req2.scheme_slug == "pm-kisan"
        assert req2.question == "How to apply?"
