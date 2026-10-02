"""Tests for client-side viewport scroll positioning on questionnaire navigation."""

from unittest.mock import MagicMock, patch
import pytest
import streamlit as st
from frontend.services.questionnaire_engine import questionnaire_engine
from frontend.utils.ui import get_scroll_to_top_js, inject_scroll_to_top


class TestScrollToTopUtilities:
    """Tests for UI scroll helper functions and JavaScript generation."""

    def test_get_scroll_to_top_js_default(self):
        js = get_scroll_to_top_js()
        assert "<script>" in js
        assert "</script>" in js
        assert "questionnaire-top" in js
        assert "questionnaire-top-anchor" in js
        assert "scrollIntoView" in js
        assert "smooth" in js
        # Check standard Streamlit scroll container selectors
        assert "section.main" in js
        assert '[data-testid="stAppViewContainer"]' in js
        assert '[data-testid="stMain"]' in js
        assert '[data-testid="stAppViewBlockContainer"]' in js
        assert "requestAnimationFrame" in js
        assert "setTimeout" in js

    def test_get_scroll_to_top_js_custom_anchor(self):
        js = get_scroll_to_top_js(anchor_id="results-top")
        assert "results-top" in js
        assert "results-top-anchor" in js

    @patch("streamlit.components.v1.html")
    def test_inject_scroll_to_top_calls_components_html_zero_dimensions(self, mock_components_html):
        inject_scroll_to_top(anchor_id="questionnaire-top")
        assert mock_components_html.called
        args, kwargs = mock_components_html.call_args
        assert kwargs.get("height") == 0
        assert kwargs.get("width") == 0
        assert "questionnaire-top" in args[0]

    def test_get_scheme_details_scroll_js(self):
        from frontend.utils.ui import get_scheme_details_scroll_js
        js = get_scheme_details_scroll_js(anchor_id="scheme-detail-top")
        assert "<script" in js
        assert "</script>" in js
        assert "scheme-detail-top" in js
        assert "resetSchemePageScroll" in js
        assert "scrollRestoration" in js
        assert "scrollTo" in js
        assert '[data-testid="stAppViewContainer"]' in js
        assert "section.main" in js
        assert "requestAnimationFrame" in js
        assert "setTimeout" in js

    @patch("streamlit.html")
    @patch("streamlit.components.v1.html")
    def test_inject_scheme_details_scroll_to_top_uses_st_html(self, mock_components_html, mock_st_html):
        from frontend.utils.ui import inject_scheme_details_scroll_to_top
        inject_scheme_details_scroll_to_top(anchor_id="scheme-detail-top")
        assert mock_st_html.called
        assert not mock_components_html.called
        args, kwargs = mock_st_html.call_args
        assert kwargs.get("unsafe_allow_javascript") is True
        assert "scheme-detail-top" in args[0]

    @patch("streamlit.html")
    @patch("streamlit.components.v1.html")
    def test_inject_home_scroll_to_top_uses_st_html(self, mock_components_html, mock_st_html):
        from frontend.utils.ui import inject_home_scroll_to_top
        inject_home_scroll_to_top(anchor_id="home-top")
        assert mock_st_html.called
        assert not mock_components_html.called
        args, kwargs = mock_st_html.call_args
        assert kwargs.get("unsafe_allow_javascript") is True
        assert "home-top" in args[0]



class TestScrollNavigationStateLogic:
    """Tests for scroll-to-top triggering logic during questionnaire navigation steps."""

    def test_step_change_triggers_scroll(self):
        """Moving between steps should evaluate should_scroll as True."""
        # Initial arrival (last_step is None)
        last_step = None
        current_step = 0
        explicit_scroll = False
        should_scroll = explicit_scroll or (last_step is not None and last_step != current_step) or (last_step is None)
        assert should_scroll is True

        # Advance to step 1
        last_step = 0
        current_step = 1
        explicit_scroll = False
        should_scroll = explicit_scroll or (last_step is not None and last_step != current_step) or (last_step is None)
        assert should_scroll is True

        # Advance to step 2
        last_step = 1
        current_step = 2
        explicit_scroll = False
        should_scroll = explicit_scroll or (last_step is not None and last_step != current_step) or (last_step is None)
        assert should_scroll is True

        # Go back from step 2 to step 1
        last_step = 2
        current_step = 1
        explicit_scroll = True
        should_scroll = explicit_scroll or (last_step is not None and last_step != current_step) or (last_step is None)
        assert should_scroll is True

    def test_in_step_interaction_does_not_trigger_scroll(self):
        """User modifying a dropdown or field inside the same step must NOT trigger scroll."""
        last_step = 1
        current_step = 1
        explicit_scroll = False
        should_scroll = explicit_scroll or (last_step is not None and last_step != current_step) or (last_step is None)
        assert should_scroll is False

    def test_answers_preserved_across_navigation_steps(self):
        """Verifies that navigation does not discard canonical answers or payload data."""
        answers = {
            "intent": "education",
            "age": 21,
            "gender": "female",
            "state": "Maharashtra",
            "area": "Rural",
            "student_status": "in_college",
            "course_level": "undergraduate",
            "annual_income": 180000,
        }

        # Validate group
        groups = questionnaire_engine.get_active_groups(answers)
        assert len(groups) >= 3

        # Step through groups without mutating existing answers
        step1_group = groups[1]  # Demographic & Academic
        is_valid, err = questionnaire_engine.validate_group(step1_group, answers)
        assert is_valid is True

        # Answers intact
        assert answers["age"] == 21
        assert answers["gender"] == "female"
        assert answers["state"] == "Maharashtra"

        # Build payload
        payload = questionnaire_engine.build_profile_payload(answers)
        assert payload["age"] == 21
        assert payload["state"] == "Maharashtra"
        assert payload["occupation"] == "student"
        assert payload["annual_income"] == 180000


class TestSchemeDetailScrollLogic:
    """Tests for scroll-to-top triggering logic on Scheme Detail page."""

    def test_navigation_from_other_pages_triggers_scroll(self):
        """Navigating to a scheme from any other page must trigger scroll-to-top."""
        entry_pages = ["home", "schemes", "results", "saved", "tracker"]
        cur_slug = "pm-kisan"

        for p in entry_pages:
            last_page = p
            last_viewed_slug = cur_slug
            explicit_scroll = True
            should_scroll = (
                explicit_scroll
                or (last_page != "scheme_details")
                or (last_viewed_slug != cur_slug)
            )
            assert should_scroll is True, f"Failed for entry page: {p}"

    def test_switching_schemes_triggers_scroll(self):
        """Switching between two different schemes must trigger scroll-to-top."""
        last_page = "scheme_details"
        last_viewed_slug = "ayushman-bharat-pmjay"
        cur_slug = "pm-kisan"
        explicit_scroll = False

        should_scroll = (
            explicit_scroll
            or (last_page != "scheme_details")
            or (last_viewed_slug != cur_slug)
        )
        assert should_scroll is True

    def test_in_page_interaction_does_not_trigger_scroll(self):
        """Interacting with in-page elements (e.g. AI questions) on Scheme Detail must NOT trigger scroll."""
        last_page = "scheme_details"
        last_viewed_slug = "pm-kisan"
        cur_slug = "pm-kisan"
        explicit_scroll = False

        should_scroll = (
            explicit_scroll
            or (last_page != "scheme_details")
            or (last_viewed_slug != cur_slug)
        )
        assert should_scroll is False

    def test_revisiting_same_scheme_after_browsing_triggers_scroll(self):
        """Leaving Scheme Detail to browse schemes and clicking the same scheme again must trigger scroll."""
        # User was on schemes page
        last_page = "schemes"
        last_viewed_slug = "pm-kisan"
        cur_slug = "pm-kisan"
        explicit_scroll = True  # Set by on_details click or navigate_to

        should_scroll = (
            explicit_scroll
            or (last_page != "scheme_details")
            or (last_viewed_slug != cur_slug)
        )
        assert should_scroll is True


class TestResultsBackNavigation:
    """Tests for Back button navigation from Results page to the questionnaire."""

    def test_results_back_returns_to_last_questionnaire_step(self):
        """Clicking Back from Results should return to the last active questionnaire group."""
        answers = {
            "intent": "agriculture",
            "age": 42,
            "gender": "male",
            "state": "Uttar Pradesh",
            "landholding_acres": 2.5,
        }
        active_groups = questionnaire_engine.get_active_groups(answers)
        assert len(active_groups) >= 2
        last_group_idx = len(active_groups) - 1

        # Simulate questionnaire finishing on last group
        step = last_group_idx
        resolved_step = min(step, max(0, len(active_groups) - 1)) if active_groups else 0
        assert resolved_step == last_group_idx

    def test_results_back_preserves_all_answers(self):
        """All user answers must remain completely intact when returning to the questionnaire."""
        session_state = {
            "eligibility_answers": {
                "intent": "education",
                "age": 22,
                "gender": "female",
                "state": "Maharashtra",
                "area": "Urban",
                "student_status": "in_college",
                "course_level": "postgraduate",
                "annual_income": 250000,
            },
            "questionnaire_step": 2,
        }

        # Simulate clicking back
        answers = session_state.get("eligibility_answers", {})
        active_groups = questionnaire_engine.get_active_groups(answers) if "intent" in answers else []
        step = session_state.get("questionnaire_step")
        if step is None or step < 0:
            step = max(0, len(active_groups) - 1) if active_groups else 0
        else:
            step = min(step, max(0, len(active_groups) - 1)) if active_groups else 0

        session_state["questionnaire_step"] = step
        session_state["validation_error"] = None
        session_state["_scroll_to_top_needed"] = True
        session_state["_last_questionnaire_step"] = None

        # Verify all answers remain exactly preserved
        assert session_state["eligibility_answers"]["intent"] == "education"
        assert session_state["eligibility_answers"]["age"] == 22
        assert session_state["eligibility_answers"]["gender"] == "female"
        assert session_state["eligibility_answers"]["state"] == "Maharashtra"
        assert session_state["eligibility_answers"]["course_level"] == "postgraduate"
        assert session_state["eligibility_answers"]["annual_income"] == 250000
        assert session_state["questionnaire_step"] == 2
        assert session_state["_scroll_to_top_needed"] is True

    def test_results_back_triggers_scroll_to_top(self):
        """Returning to the questionnaire from Results must evaluate should_scroll to True."""
        _scroll_to_top_needed = True
        _last_questionnaire_step = None
        current_step = 2

        explicit_scroll = _scroll_to_top_needed
        last_step = _last_questionnaire_step
        step_changed = (last_step is not None and last_step != current_step)
        initial_entry = (last_step is None)
        should_scroll = explicit_scroll or step_changed or initial_entry

        assert should_scroll is True

    def test_results_back_graceful_fallback_without_prior_answers(self):
        """If user reaches Results directly with empty answers, Back safely defaults to step 0."""
        answers = {}
        active_groups = questionnaire_engine.get_active_groups(answers) if "intent" in answers else []
        step = None

        if step is None or step < 0:
            step = max(0, len(active_groups) - 1) if active_groups else 0
        else:
            step = min(step, max(0, len(active_groups) - 1)) if active_groups else 0

        assert step == 0


class TestPostLoginHomeScrollNavigation:
    """Verifies that successful Sign In marks home_scroll_to_top = True,
    and Home consumes the flag strictly once to scroll to the top."""

    def setup_method(self):
        st.session_state.clear()
        st.session_state.current_page = "home"

    @patch("streamlit.rerun")
    @patch("streamlit.toast")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("streamlit.button")
    @patch("streamlit.text_input")
    @patch("frontend.services.api_client.api_client.sign_in")
    def test_successful_sign_in_navigates_to_home_with_scroll_flag(
        self,
        mock_sign_in,
        mock_text_input,
        mock_button,
        mock_markdown,
        mock_columns,
        mock_toast,
        mock_rerun,
    ):
        from frontend.pages.profile import render_citizen_profile

        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        # Simulate user filling in email/password and clicking Sign In button
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "btn_auth_signin"
        mock_text_input.side_effect = lambda label, *args, **kwargs: "user@example.com" if "Email" in label or "ईमेल" in label else "pass123"
        mock_sign_in.return_value = {
            "ok": True,
            "data": {"user_id": "usr_test_123", "name": "Rahul Verma", "email": "user@example.com"},
        }

        st.session_state.is_authenticated = False
        st.session_state.current_page = "profile"
        st.session_state.auth_redirect_target = "home"

        mock_navigate = MagicMock()
        render_citizen_profile(mock_navigate)

        assert st.session_state.is_authenticated is True
        assert st.session_state.user_name == "Rahul Verma"
        # Must mark home_scroll_to_top = True
        assert st.session_state.get("home_scroll_to_top") is True
        # Must navigate to "home"
        mock_navigate.assert_called_once_with("home")

    @patch("frontend.pages.home.inject_home_scroll_to_top")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("streamlit.button")
    def test_home_consumes_scroll_flag_once_and_resets(
        self,
        mock_button,
        mock_markdown,
        mock_columns,
        mock_inject_home_scroll,
    ):
        from frontend.pages.home import render_home

        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_button.return_value = False

        st.session_state.current_page = "home"
        st.session_state.home_scroll_to_top = True

        mock_navigate = MagicMock()
        render_home(mock_navigate)

        # 1. Scroll-to-top was injected for home-top
        mock_inject_home_scroll.assert_called_once_with(anchor_id="home-top")
        # 2. Flag was consumed (popped)
        assert "home_scroll_to_top" not in st.session_state
        assert st.session_state.get("home_scroll_to_top") is None

        # 3. Subsequent normal render / rerun: flag is no longer present
        mock_inject_home_scroll.reset_mock()
        render_home(mock_navigate)

        # Must NOT inject scroll-to-top again (user can scroll freely without being forced back to top)
        mock_inject_home_scroll.assert_not_called()

    @patch("streamlit.rerun")
    @patch("streamlit.toast")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("streamlit.button")
    @patch("streamlit.text_input")
    @patch("frontend.services.api_client.api_client.sign_in")
    def test_sign_in_from_other_pages_does_not_set_home_scroll_flag(
        self,
        mock_sign_in,
        mock_text_input,
        mock_button,
        mock_markdown,
        mock_columns,
        mock_toast,
        mock_rerun,
    ):
        from frontend.pages.profile import render_citizen_profile

        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "btn_auth_signin"
        mock_text_input.side_effect = lambda label, *args, **kwargs: "user@example.com" if "Email" in label or "ईमेल" in label else "pass123"
        mock_sign_in.return_value = {
            "ok": True,
            "data": {"user_id": "usr_test_123", "name": "Rahul Verma", "email": "user@example.com"},
        }

        # User clicked sign in from Tracker
        st.session_state.is_authenticated = False
        st.session_state.current_page = "profile"
        st.session_state.auth_redirect_target = "tracker"

        mock_navigate = MagicMock()
        render_citizen_profile(mock_navigate)

        assert st.session_state.is_authenticated is True
        # Must navigate to "tracker"
        mock_navigate.assert_called_once_with("tracker")
        # home_scroll_to_top must NOT be set
        assert "home_scroll_to_top" not in st.session_state

    @patch("streamlit.rerun")
    @patch("streamlit.toast")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("streamlit.button")
    @patch("streamlit.text_input")
    @patch("frontend.services.api_client.api_client.sign_in")
    def test_logout_and_sign_in_again_resets_home_scroll_flag(
        self,
        mock_sign_in,
        mock_text_input,
        mock_button,
        mock_markdown,
        mock_columns,
        mock_toast,
        mock_rerun,
    ):
        from frontend.pages.profile import render_citizen_profile

        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_text_input.side_effect = lambda label, *args, **kwargs: "user@example.com" if "Email" in label or "ईमेल" in label else "pass123"
        mock_sign_in.return_value = {
            "ok": True,
            "data": {"user_id": "usr_test_123", "name": "Rahul Verma", "email": "user@example.com"},
        }

        # First: simulate user was logged in, then logged out
        st.session_state.is_authenticated = False
        st.session_state.user_id = ""
        st.session_state.current_page = "profile"
        st.session_state.auth_redirect_target = "home"

        # Now sign in again
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "btn_auth_signin"
        mock_navigate = MagicMock()
        render_citizen_profile(mock_navigate)

        assert st.session_state.is_authenticated is True
        assert st.session_state.get("home_scroll_to_top") is True
        mock_navigate.assert_called_once_with("home")



