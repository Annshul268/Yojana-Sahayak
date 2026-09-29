"""Tests for Citizen Profile Auto-Fill, Session Reset, and In-App Back Navigation."""

from unittest.mock import MagicMock, patch
import pytest
import streamlit as st

from frontend.pages.profile import render_citizen_profile
from frontend.pages.saved import render_saved_schemes
from frontend.pages.scheme_details import render_scheme_details
from frontend.pages.schemes import render_schemes_directory
from frontend.pages.tracker import render_application_tracker
from frontend.pages.scheme_finder import (
    apply_profile_to_answers,
    handle_auto_fill,
    handle_manual_fill,
    reset_eligibility_session,
    _on_dialog_dismiss,
)
from frontend.services.questionnaire_engine import questionnaire_engine


class TestNavigationBackButtons:
    """Tests in-app Back button navigation for schemes, tracker, and profile pages."""

    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    def test_schemes_directory_back_button_navigates_to_last_page(
        self, mock_markdown, mock_columns, mock_button
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "schemes_dir_back_btn"

        navigate_mock = MagicMock()
        st.session_state["_last_rendered_page"] = "home"

        render_schemes_directory(navigate_mock)
        navigate_mock.assert_called_with("home")

    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    def test_schemes_directory_back_button_fallback_to_home(
        self, mock_markdown, mock_columns, mock_button
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "schemes_dir_back_btn"

        navigate_mock = MagicMock()
        st.session_state["_last_rendered_page"] = "schemes"

        render_schemes_directory(navigate_mock)
        navigate_mock.assert_called_with("home")

    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    def test_tracker_back_button_navigates_to_last_page(
        self, mock_markdown, mock_columns, mock_button
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "tracker_back_btn"

        navigate_mock = MagicMock()
        st.session_state["_last_rendered_page"] = "results"

        render_application_tracker(navigate_mock)
        navigate_mock.assert_called_with("results")

    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("frontend.services.api_client.api_client.get_profile")
    def test_profile_back_button_navigates_to_last_page(
        self, mock_get_profile, mock_markdown, mock_columns, mock_button
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "profile_back_btn"
        mock_get_profile.return_value = {"ok": True, "data": {}}

        navigate_mock = MagicMock()
        st.session_state.is_authenticated = True
        st.session_state["_last_rendered_page"] = "home"

        render_citizen_profile(navigate_mock)
        navigate_mock.assert_called_with("home")

    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("frontend.services.api_client.api_client.list_saved")
    def test_saved_schemes_back_button_navigates_to_last_page(
        self, mock_list_saved, mock_markdown, mock_columns, mock_button
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "saved_back_btn"
        mock_list_saved.return_value = {"ok": True, "data": []}

        navigate_mock = MagicMock()
        st.session_state["_last_rendered_page"] = "profile"

        render_saved_schemes(navigate_mock)
        navigate_mock.assert_called_with("profile")

    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("frontend.services.api_client.api_client.list_saved")
    def test_saved_schemes_back_button_fallback_to_home(
        self, mock_list_saved, mock_markdown, mock_columns, mock_button
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "saved_back_btn"
        mock_list_saved.return_value = {"ok": True, "data": []}

        navigate_mock = MagicMock()
        st.session_state["_last_rendered_page"] = "saved"

        render_saved_schemes(navigate_mock)
        navigate_mock.assert_called_with("home")

    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("frontend.services.api_client.api_client.get_scheme")
    def test_scheme_details_back_button_source_aware_navigation(
        self, mock_get_scheme, mock_markdown, mock_columns, mock_button
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "scheme_det_back_btn"
        mock_get_scheme.return_value = {
            "ok": True,
            "data": {
                "id": "pm-kisan-id",
                "slug": "pm-kisan",
                "name": "PM Kisan",
                "category": "Agriculture",
                "benefits": ["Benefit 1"],
                "documents": ["Doc 1"],
                "application_steps": ["Step 1"],
            }
        }

        navigate_mock = MagicMock()
        st.session_state["selected_scheme_slug"] = "pm-kisan"
        st.session_state["scheme_navigation_source"] = "featured"

        render_scheme_details(navigate_mock)
        navigate_mock.assert_called_with("home")
        assert "scheme_navigation_source" not in st.session_state
        assert "selected_scheme_slug" not in st.session_state

    @patch("streamlit.rerun")
    @patch("streamlit.toast")
    @patch("streamlit.link_button")
    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("frontend.services.api_client.api_client.remove_saved_scheme")
    @patch("frontend.services.api_client.api_client.list_saved")
    def test_saved_schemes_remove_button_has_no_emoji_and_triggers_removal(
        self,
        mock_list_saved,
        mock_remove_saved,
        mock_markdown,
        mock_columns,
        mock_button,
        mock_link_button,
        mock_toast,
        mock_rerun,
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_list_saved.return_value = {
            "ok": True,
            "data": [
                {
                    "scheme": {
                        "id": "scheme_101",
                        "slug": "pm-kisan",
                        "name": "PM Kisan Samman Nidhi",
                        "category": "Agriculture",
                        "official_url": "https://pmkisan.gov.in",
                    }
                }
            ],
        }

        # Track labels of rendered buttons
        button_labels = []

        def handle_button(label, *args, **kwargs):
            button_labels.append(label)
            if kwargs.get("key") == "saved_rem_pm-kisan":
                return True
            return False

        mock_button.side_effect = handle_button

        st.session_state["user_id"] = "test_user_42"
        render_saved_schemes(MagicMock())

        # Verify "Remove" button label is clean and has no dustbin or other emojis
        assert "Remove" in button_labels
        assert not any("🗑" in lbl for lbl in button_labels)
        mock_remove_saved.assert_called_once_with(scheme_id="scheme_101", user_id="test_user_42")
        mock_toast.assert_called_once_with("Removed from bookmarks")
        mock_rerun.assert_called_once()


class TestSessionReset:
    """Tests session clearing and answer isolation between separate searches."""

    def test_reset_eligibility_session_clears_all_state(self):
        st.session_state.eligibility_answers = {"state": "Delhi", "age": 25}
        st.session_state.adaptive_answers = st.session_state.eligibility_answers
        st.session_state.match_results = {"results": [1, 2, 3]}
        st.session_state.matched_profile = {"age": 25}
        st.session_state.validation_error = "Old Error"
        st.session_state.pending_category_intent = "education"
        st.session_state.field_state = "Delhi"
        st.session_state.field_age = 25.0
        st.session_state.other_key = "keep_me"

        reset_eligibility_session()

        assert st.session_state.eligibility_answers == {}
        assert st.session_state.adaptive_answers == {}
        assert "match_results" not in st.session_state
        assert "matched_profile" not in st.session_state
        assert "field_state" not in st.session_state
        assert "field_age" not in st.session_state
        assert st.session_state.get("other_key") == "keep_me"
        assert st.session_state.questionnaire_step == 0
        assert st.session_state.validation_error is None

    def test_reset_eligibility_session_keep_intent(self):
        st.session_state.field_state = "Punjab"
        st.session_state.field_age = 30.0

        reset_eligibility_session(keep_intent="agriculture")

        assert st.session_state.eligibility_answers == {"intent": "agriculture"}
        assert st.session_state.questionnaire_step == 1
        assert "field_state" not in st.session_state
        assert "field_age" not in st.session_state


class TestProfileAutoFillMapping:
    """Tests mapping of citizen profile attributes to questionnaire fields."""

    def test_apply_profile_to_answers_complete(self):
        profile_data = {
            "name": "Priya Sharma",
            "state": "Maharashtra",
            "district": "Pune",
            "area": "Urban",
            "age": 28,
            "gender": "Female",
            "annual_income": 350000.0,
            "category": "OBC",
            "disability": False,
            "marital_status": "single",
            "minority_status": False,
            "occupation": "salaried",
        }
        answers = {"intent": "business"}

        apply_profile_to_answers(profile_data, answers)

        assert answers["intent"] == "business"
        assert answers["state"] == "Maharashtra"
        assert answers["district"] == "Pune"
        assert answers["area"] == "Urban"
        assert answers["age"] == 28.0
        assert answers["gender"] == "female"
        assert answers["annual_income"] == 350000.0
        assert answers["social_category"] == "OBC"
        assert answers["disability"] == "no"
        assert answers["marital_status"] == "single"
        assert answers["minority_status"] == "no"
        assert answers["occupation"] == "salaried"

    def test_apply_profile_to_answers_partial_and_missing(self):
        profile_data = {
            "state": "Bihar",
            "age": 42,
            "gender": "Male",
        }
        answers = {}

        apply_profile_to_answers(profile_data, answers)

        assert answers["state"] == "Bihar"
        assert answers["age"] == 42.0
        assert answers["gender"] == "male"
        # Missing fields in profile must NOT be set
        assert "district" not in answers
        assert "area" not in answers
        assert "annual_income" not in answers
        assert "social_category" not in answers
        assert "disability" not in answers

    def test_apply_profile_to_answers_does_not_mutate_profile(self):
        original_profile = {
            "state": "Karnataka",
            "age": 22,
            "gender": "Other / Transgender",
            "category": "SC",
            "disability": True,
        }
        profile_copy = dict(original_profile)
        answers = {}

        apply_profile_to_answers(original_profile, answers)

        # Profile dict should not have been mutated
        assert original_profile == profile_copy
        assert answers["gender"] == "other"
        assert answers["disability"] == "yes"
        assert answers["social_category"] == "SC"

    def test_apply_profile_empty(self):
        answers = {"intent": "education"}
        apply_profile_to_answers({}, answers)
        assert answers == {"intent": "education"}


class TestDialogFlows:
    """Tests manual vs autofill handler behaviors."""

    @patch("streamlit.rerun")
    def test_handle_manual_fill(self, mock_rerun):
        st.session_state.eligibility_answers = {"state": "Delhi", "age": 50}
        st.session_state.field_state = "Delhi"

        handle_manual_fill("education")

        assert st.session_state.fill_mode == "manual"
        assert st.session_state.eligibility_answers == {"intent": "education"}
        assert "field_state" not in st.session_state
        assert st.session_state.questionnaire_step == 1
        assert "pending_category_intent" not in st.session_state
        mock_rerun.assert_called_once()

    @patch("streamlit.rerun")
    @patch("frontend.services.api_client.api_client.get_profile")
    def test_handle_auto_fill(self, mock_get_profile, mock_rerun):
        mock_get_profile.return_value = {
            "ok": True,
            "data": {
                "state": "Gujarat",
                "age": 35,
                "gender": "Male",
                "annual_income": 180000,
                "category": "EWS",
                "area": "Rural",
                "disability": False,
            },
        }

        st.session_state.field_state = "Delhi"

        handle_auto_fill("agriculture")

        assert st.session_state.fill_mode == "autofill"
        assert st.session_state.eligibility_answers["intent"] == "agriculture"
        assert st.session_state.eligibility_answers["state"] == "Gujarat"
        assert st.session_state.eligibility_answers["age"] == 35.0
        assert st.session_state.eligibility_answers["gender"] == "male"
        assert st.session_state.eligibility_answers["annual_income"] == 180000.0
        assert st.session_state.eligibility_answers["social_category"] == "EWS"
        assert st.session_state.eligibility_answers["area"] == "Rural"
        assert st.session_state.eligibility_answers["disability"] == "no"
        assert "field_state" not in st.session_state
        assert st.session_state.questionnaire_step == 1
        assert "pending_category_intent" not in st.session_state
        mock_rerun.assert_called_once()

    def test_on_dialog_dismiss(self):
        st.session_state.pending_category_intent = "education"
        _on_dialog_dismiss()
        assert "pending_category_intent" not in st.session_state
