"""Tests for Featured Schemes Carousel Navigation and Grounded AI Explain functionality."""

import os
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from frontend.components.featured_carousel import render_featured_carousel
from frontend.services.api_client import APIClient, get_backend_api_url
from backend.app.ai.service import AIService
from backend.app.schemas.ai import AskAIRequest, ExplainEligibilityRequest


class TestFeaturedCarouselRenderingAndNavigation:
    """Verifies that the featured carousel renders proper Streamlit-compatible navigation and state synchronization."""

    @pytest.fixture
    def sample_schemes(self):
        return [
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

    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    def test_carousel_renders_synchronized_active_scheme(self, mock_markdown, mock_columns, mock_button, sample_schemes):
        import streamlit as st
        st.session_state["featured_carousel_index"] = 0
        st.session_state["_carousel_last_tick"] = 1000.0
        st.session_state["selected_scheme_slug"] = None

        mock_columns.side_effect = lambda spec, *args, **kwargs: [MagicMock() for _ in range(len(spec))]
        mock_button.return_value = False

        carousel_fn = getattr(render_featured_carousel, "__wrapped__", render_featured_carousel)
        with patch("time.time", return_value=1001.0):
            carousel_fn(sample_schemes, lang="en")

        # Check markdown calls for card and image link
        markdown_calls = [c[0][0] for c in mock_markdown.call_args_list]
        card_html = next(html for html in markdown_calls if '<div class="carousel-card-wrap">' in html)

        # Image must link to official_url in a new tab, NOT to internal Scheme Detail
        assert 'href="https://pmkisan.gov.in"' in card_html
        assert 'target="_blank"' in card_html
        assert 'rel="noopener noreferrer"' in card_html
        assert "PM Kisan Samman Nidhi" in card_html
        assert "Financial support to farmer families." in card_html
        assert "Agriculture" in card_html
        assert "Central Scheme" in card_html

    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    def test_carousel_image_url_synchronization_per_slide(self, mock_markdown, mock_columns, mock_button, sample_schemes):
        import streamlit as st
        carousel_fn = getattr(render_featured_carousel, "__wrapped__", render_featured_carousel)
        mock_columns.side_effect = lambda spec, *args, **kwargs: [MagicMock() for _ in range(len(spec))]
        mock_button.return_value = False

        # Slide 0: PM Kisan
        st.session_state["featured_carousel_index"] = 0
        st.session_state["_carousel_last_tick"] = 1000.0
        mock_markdown.reset_mock()
        with patch("time.time", return_value=1001.0):
            carousel_fn(sample_schemes, lang="en")
        card_html_0 = next(html for html in [c[0][0] for c in mock_markdown.call_args_list] if '<div class="carousel-card-wrap">' in html)
        assert 'href="https://pmkisan.gov.in"' in card_html_0

        # Slide 1: Ayushman Bharat
        st.session_state["featured_carousel_index"] = 1
        st.session_state["_carousel_last_tick"] = 1000.0
        mock_markdown.reset_mock()
        with patch("time.time", return_value=1001.0):
            carousel_fn(sample_schemes, lang="en")
        card_html_1 = next(html for html in [c[0][0] for c in mock_markdown.call_args_list] if '<div class="carousel-card-wrap">' in html)
        assert 'href="https://pmjay.gov.in"' in card_html_1

        # Slide 2: PMAY Gramin
        st.session_state["featured_carousel_index"] = 2
        st.session_state["_carousel_last_tick"] = 1000.0
        mock_markdown.reset_mock()
        with patch("time.time", return_value=1001.0):
            carousel_fn(sample_schemes, lang="en")
        card_html_2 = next(html for html in [c[0][0] for c in mock_markdown.call_args_list] if '<div class="carousel-card-wrap">' in html)
        assert 'href="https://pmayg.nic.in"' in card_html_2

    @patch("streamlit.rerun")
    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    def test_carousel_next_arrow_navigation(self, mock_markdown, mock_columns, mock_button, mock_rerun, sample_schemes):
        import streamlit as st
        st.session_state["featured_carousel_index"] = 0
        st.session_state["_carousel_last_tick"] = 1000.0
        st.session_state["selected_scheme_slug"] = None

        mock_columns.side_effect = lambda spec, *args, **kwargs: [MagicMock() for _ in range(len(spec))]
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "feat_next_0"

        carousel_fn = getattr(render_featured_carousel, "__wrapped__", render_featured_carousel)
        with patch("time.time", return_value=1001.0):
            carousel_fn(sample_schemes, lang="en")

        assert st.session_state.featured_carousel_index == 1
        mock_rerun.assert_called_once_with(scope="fragment")

    @patch("streamlit.rerun")
    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    def test_carousel_prev_arrow_navigation(self, mock_markdown, mock_columns, mock_button, mock_rerun, sample_schemes):
        import streamlit as st
        st.session_state["featured_carousel_index"] = 0
        st.session_state["_carousel_last_tick"] = 1000.0
        st.session_state["selected_scheme_slug"] = None

        mock_columns.side_effect = lambda spec, *args, **kwargs: [MagicMock() for _ in range(len(spec))]
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "feat_prev_0"

        carousel_fn = getattr(render_featured_carousel, "__wrapped__", render_featured_carousel)
        with patch("time.time", return_value=1001.0):
            carousel_fn(sample_schemes, lang="en")

        # Loops from 0 backwards to 2 (last scheme)
        assert st.session_state.featured_carousel_index == 2
        mock_rerun.assert_called_once_with(scope="fragment")

    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    def test_carousel_view_scheme_button_navigation(self, mock_markdown, mock_columns, mock_button, sample_schemes):
        import streamlit as st
        st.session_state["featured_carousel_index"] = 1
        st.session_state["_carousel_last_tick"] = 1000.0
        st.session_state["selected_scheme_slug"] = None

        mock_columns.side_effect = lambda spec, *args, **kwargs: [MagicMock() for _ in range(len(spec))]
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "feat_view_1_ayushman-bharat-pmjay"

        navigate_mock = MagicMock()
        carousel_fn = getattr(render_featured_carousel, "__wrapped__", render_featured_carousel)
        with patch("time.time", return_value=1001.0):
            carousel_fn(sample_schemes, lang="en", navigate_to=navigate_mock)

        assert st.session_state.selected_scheme_slug == "ayushman-bharat-pmjay"
        assert st.session_state.scheme_navigation_source == "featured"
        navigate_mock.assert_called_once_with("scheme_details")

    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    def test_carousel_auto_scroll_tick_advances_scheme(self, mock_markdown, mock_columns, mock_button, sample_schemes):
        import streamlit as st
        st.session_state["featured_carousel_index"] = 0
        st.session_state["_carousel_last_tick"] = 1000.0
        st.session_state["selected_scheme_slug"] = None

        mock_columns.side_effect = lambda spec, *args, **kwargs: [MagicMock() for _ in range(len(spec))]
        mock_button.return_value = False

        carousel_fn = getattr(render_featured_carousel, "__wrapped__", render_featured_carousel)
        # When 4.5 seconds elapse, timer advances index
        with patch("time.time", return_value=1004.5):
            carousel_fn(sample_schemes, lang="en")

        assert st.session_state.featured_carousel_index == 1

    @pytest.mark.parametrize("source,expected_target", [
        ("featured", "home"),
        ("home", "home"),
        ("all_schemes", "schemes"),
        ("schemes", "schemes"),
        ("saved", "saved"),
        ("saved_schemes", "saved"),
        ("applications", "tracker"),
        ("tracker", "tracker"),
        ("results", "results"),
        ("finder", "finder"),
        ("profile", "profile"),
        (None, "home"),
    ])
    @patch("frontend.services.api_client.api_client.get_scheme")
    @patch("streamlit.columns")
    @patch("streamlit.button")
    @patch("streamlit.markdown")
    def test_scheme_details_source_aware_back_navigation(self, mock_markdown, mock_button, mock_columns, mock_get_scheme, source, expected_target):
        from frontend.pages.scheme_details import render_scheme_details
        import streamlit as st

        st.session_state["selected_scheme_slug"] = "pm-kisan"
        if source is not None:
            st.session_state["scheme_navigation_source"] = source
        else:
            st.session_state.pop("scheme_navigation_source", None)
            st.session_state.pop("_last_rendered_page", None)

        mock_columns.side_effect = lambda spec, *args, **kwargs: [MagicMock() for _ in range(spec if isinstance(spec, int) else len(spec))]
        # Simulate clicking the Back button
        mock_button.side_effect = lambda label, *args, **kwargs: "Back" in str(label) or "वापस" in str(label)
        mock_get_scheme.return_value = {"ok": True, "data": {"id": "1", "name": "PM Kisan", "slug": "pm-kisan"}}

        mock_navigate = MagicMock()
        render_scheme_details(mock_navigate)

        mock_navigate.assert_called_once_with(expected_target)
        assert "scheme_navigation_source" not in st.session_state


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
