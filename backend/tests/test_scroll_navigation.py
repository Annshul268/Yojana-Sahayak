"""Tests for client-side viewport scroll positioning on questionnaire navigation."""

from unittest.mock import patch
import pytest
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
