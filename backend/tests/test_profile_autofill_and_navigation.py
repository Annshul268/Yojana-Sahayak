"""Tests for Citizen Profile Auto-Fill, Session Reset, and In-App Back Navigation."""

from unittest.mock import MagicMock, patch
import pytest
import streamlit as st

from frontend.pages.home import render_home
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

    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    def test_home_does_not_render_when_not_on_home_page(
        self, mock_markdown, mock_columns, mock_button
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        navigate_mock = MagicMock()
        old_page = st.session_state.get("current_page", "home")
        try:
            st.session_state["current_page"] = "schemes"
            render_home(navigate_mock)
            assert mock_markdown.call_count == 0
            assert mock_button.call_count == 0
            navigate_mock.assert_not_called()
        finally:
            st.session_state["current_page"] = old_page

    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    def test_home_browse_schemes_button_stops_execution_immediately(
        self, mock_markdown, mock_columns, mock_button
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        # Return True for hero_browse_schemes_btn
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "hero_browse_schemes_btn"

        navigate_mock = MagicMock()
        old_page = st.session_state.get("current_page", "home")
        try:
            st.session_state["current_page"] = "home"
            # When clicked, navigate_to("schemes") is called and render_home returns early
            def mock_nav(target):
                st.session_state["current_page"] = target
                navigate_mock(target)

            render_home(mock_nav)
            navigate_mock.assert_called_once_with("schemes")
            assert st.session_state["current_page"] == "schemes"
        finally:
            st.session_state["current_page"] = old_page

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


class TestNavigationCallbackSafety:
    """Tests that navigation functions behave safely inside and outside callbacks."""

    @patch("frontend.app.is_in_callback", return_value=True)
    @patch("streamlit.rerun")
    def test_navigate_to_inside_callback_updates_state_without_rerun(self, mock_rerun, mock_in_cb):
        from frontend.app import navigate_to
        st.session_state.current_page = "home"
        navigate_to("schemes")
        assert st.session_state.current_page == "schemes"
        mock_rerun.assert_not_called()

    @patch("frontend.app.is_in_callback", return_value=False)
    @patch("streamlit.rerun")
    def test_navigate_to_outside_callback_calls_rerun(self, mock_rerun, mock_in_cb):
        from frontend.app import navigate_to
        st.session_state.current_page = "home"
        navigate_to("schemes")
        assert st.session_state.current_page == "schemes"
        mock_rerun.assert_called_once()

    def test_apptest_navigation_clean_transitions(self):
        import subprocess, sys
        code = """
from pathlib import Path
from streamlit.testing.v1 import AppTest
app_path = Path('frontend/app.py')
at = AppTest.from_file(str(app_path), default_timeout=30)
at.run()
assert at.session_state.current_page == 'home'
browse_btn = [b for b in at.button if b.key == 'hero_browse_schemes_btn'][0]
browse_btn.click().run()
assert at.session_state.current_page == 'schemes'
assert len(at.warning) == 0
apps_btn = [b for b in at.button if b.key == 'nav_apps_btn'][0]
apps_btn.click().run()
assert at.session_state.current_page == 'tracker'
assert len(at.warning) == 0
"""
        res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        assert res.returncode == 0, f"AppTest failed:\n{res.stdout}\n{res.stderr}"


class TestMobileNavbarLayout:
    """Tests mobile navbar rendering, auth default state, and CSS integrity."""

    def test_apptest_auth_defaults_unauthenticated(self):
        import subprocess, sys
        code = """
from pathlib import Path
from streamlit.testing.v1 import AppTest
app_path = Path('frontend/app.py')
at = AppTest.from_file(str(app_path), default_timeout=30)
at.run()
assert at.session_state.is_authenticated is False
assert at.session_state.user_name is None
# Verify mobile navbar auth button shows Sign In when logged out
auth_btn = [b for b in at.button if b.key == 'mob_nav_auth_btn'][0]
assert auth_btn.label == 'Sign In'
"""
        res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        assert res.returncode == 0, f"AppTest failed:\n{res.stdout}\n{res.stderr}"

    def test_mobile_navbar_css_no_column2_overflow_hidden(self):
        css_path = "frontend/styles/main.css"
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        # Ensure Column 2 does not have overflow: hidden
        import re
        col2_blocks = re.findall(r'(\.st-key-mobile_nav_wrapper[^\{]*:nth-child\(2\)[^\{]*\{[^}]*\})', css)
        for block in col2_blocks:
            assert "overflow: hidden" not in block, f"Column 2 should not have overflow: hidden: {block}"
            assert "overflow: visible" in block, f"Column 2 should have overflow: visible: {block}"


class TestAuthAwareAutoFillAndReturnFlow:
    """Tests authentication-aware Auto Fill, context preservation, and seamless return."""

    def test_store_and_clear_auth_return_context(self):
        from frontend.pages.scheme_finder import store_auth_return_context, clear_auth_return_context
        st.session_state.clear()
        store_auth_return_context(
            category="education",
            step=2,
            answers={"intent": "education", "age": 21.0, "gender": "male"},
            mode="autofill",
        )
        assert st.session_state.get("auth_return_page") == "finder"
        assert st.session_state.get("auth_return_category") == "education"
        assert st.session_state.get("auth_return_step") == 2
        assert st.session_state.get("auth_return_answers") == {
            "intent": "education",
            "age": 21.0,
            "gender": "male",
        }
        assert st.session_state.get("auth_return_mode") == "autofill"

        clear_auth_return_context()
        assert "auth_return_page" not in st.session_state
        assert "auth_return_category" not in st.session_state
        assert "auth_return_step" not in st.session_state
        assert "auth_return_answers" not in st.session_state

    def test_autofill_preserves_existing_manual_inputs(self):
        profile_data = {
            "state": "Maharashtra",
            "age": 45,
            "gender": "Female",
            "annual_income": 500000.0,
            "category": "General",
        }
        # User already manually answered Age=22 and Gender=male before Auto Fill
        answers = {
            "intent": "education",
            "age": 22.0,
            "gender": "male",
        }
        apply_profile_to_answers(profile_data, answers, overwrite=False)

        # Existing manual answers must NOT be overwritten
        assert answers["age"] == 22.0
        assert answers["gender"] == "male"
        # Missing answers from profile MUST be populated
        assert answers["state"] == "Maharashtra"
        assert answers["annual_income"] == 500000.0
        assert answers["social_category"] == "General"

    @patch("streamlit.rerun")
    @patch("streamlit.toast")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("streamlit.button")
    @patch("streamlit.text_input")
    @patch("frontend.services.api_client.api_client.sign_in")
    @patch("frontend.services.api_client.api_client.get_profile")
    def test_profile_signin_redirects_to_finder_when_profile_exists(
        self, mock_get_profile, mock_sign_in, mock_text_input, mock_button, mock_markdown, mock_columns, mock_toast, mock_rerun
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "btn_auth_signin"
        mock_sign_in.return_value = {
            "ok": True,
            "data": {"user_id": "real_citizen_101", "name": "Aarav Sharma", "email": "aarav@example.com"},
        }
        mock_get_profile.return_value = {
            "ok": True,
            "data": {"name": "Aarav Sharma", "state": "Delhi", "age": 25, "gender": "Male"},
        }

        st.session_state.clear()
        st.session_state["auth_return_page"] = "finder"
        st.session_state["auth_return_category"] = "education"
        st.session_state["auth_return_step"] = 1

        nav_mock = MagicMock()
        render_citizen_profile(nav_mock)

        # Should navigate directly back to finder!
        nav_mock.assert_called_with("finder")
        assert st.session_state.is_authenticated is True
        assert st.session_state.user_id == "real_citizen_101"

    @patch("streamlit.rerun")
    @patch("streamlit.toast")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("streamlit.button")
    @patch("streamlit.text_input")
    @patch("frontend.services.api_client.api_client.sign_in")
    @patch("frontend.services.api_client.api_client.get_profile")
    def test_profile_signin_stays_for_new_user_without_profile(
        self, mock_get_profile, mock_sign_in, mock_text_input, mock_button, mock_markdown, mock_columns, mock_toast, mock_rerun
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "btn_auth_signin"
        mock_sign_in.return_value = {
            "ok": True,
            "data": {"user_id": "new_citizen_202", "name": "Priya Patel", "email": "priya@example.com"},
        }
        mock_get_profile.return_value = {"ok": True, "data": {}}

        st.session_state.clear()
        st.session_state["auth_return_page"] = "finder"
        st.session_state["auth_return_category"] = "education"

        nav_mock = MagicMock()
        render_citizen_profile(nav_mock)

        # Should NOT navigate to finder yet since profile is incomplete
        nav_mock.assert_not_called()
        mock_rerun.assert_called_once()
        assert st.session_state.is_authenticated is True
        assert st.session_state.user_id == "new_citizen_202"

    @patch("streamlit.rerun")
    @patch("streamlit.toast")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("streamlit.button")
    @patch("streamlit.text_input")
    @patch("frontend.services.api_client.api_client.register_user")
    def test_profile_signup_flow_creates_authenticated_account(
        self, mock_register_user, mock_text_input, mock_button, mock_markdown, mock_columns, mock_toast, mock_rerun
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "btn_auth_signup"
        mock_register_user.return_value = {
            "ok": True,
            "data": {"user_id": "registered_user_303", "name": "Rahul Kumar", "email": "rahul@example.com"},
        }

        st.session_state.clear()
        st.session_state["auth_mode"] = "sign_up"

        nav_mock = MagicMock()
        render_citizen_profile(nav_mock)

        assert st.session_state.is_authenticated is True
        assert st.session_state.user_id == "registered_user_303"
        assert st.session_state.user_name == "Rahul Kumar"
        mock_rerun.assert_called_once()

    @patch("streamlit.rerun")
    def test_guest_manual_fill_does_not_prompt_for_auth(self, mock_rerun):
        st.session_state.clear()
        st.session_state.is_authenticated = False
        handle_manual_fill("agriculture")

        assert st.session_state.fill_mode == "manual"
        assert st.session_state.eligibility_answers == {"intent": "agriculture"}
        assert st.session_state.questionnaire_step == 1
        assert "autofill_prompt_active" not in st.session_state
        assert "auth_return_page" not in st.session_state


class TestAuthServiceValidation:
    """Tests realistic validation rules in AuthService."""

    def test_auth_service_registration_validation(self):
        from frontend.services.auth_service import auth_service

        # Empty name
        ok, msg, _ = auth_service.register_user("", "test@example.com", "pass123", "pass123")
        assert ok is False
        assert msg == "Please enter your name."

        # Invalid email
        ok, msg, _ = auth_service.register_user("User", "invalid-email", "pass123", "pass123")
        assert ok is False
        assert msg == "Please enter a valid email address."

        # Empty password
        ok, msg, _ = auth_service.register_user("User", "user@example.com", "", "")
        assert ok is False
        assert msg == "Please enter a password."

        # Short password
        ok, msg, _ = auth_service.register_user("User", "user@example.com", "123", "123")
        assert ok is False
        assert msg == "Password must be at least 6 characters."

        # Passwords mismatch
        ok, msg, _ = auth_service.register_user("User", "user@example.com", "pass123", "different")
        assert ok is False
        assert msg == "Passwords do not match."

    def test_auth_service_login_validation(self):
        from frontend.services.auth_service import auth_service

        # Invalid email
        ok, msg, _ = auth_service.authenticate_user("not-an-email", "password123")
        assert ok is False
        assert msg == "Please enter a valid email address."

        # Empty password
        ok, msg, _ = auth_service.authenticate_user("valid@example.com", "")
        assert ok is False
        assert msg == "Please enter your password."

        # Non-existent user
        ok, msg, _ = auth_service.authenticate_user("doesnotexist999@example.com", "password123")
        assert ok is False
        assert msg == "Incorrect email or password."

    def test_auth_service_end_to_end_flow(self):
        import uuid
        from frontend.services.auth_service import auth_service

        unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        # 1. Register
        ok, msg, user = auth_service.register_user("Test Citizen Real", unique_email, "securepass123", "securepass123")
        assert ok is True
        assert user["name"] == "Test Citizen Real"
        assert user["email"] == unique_email
        assert user["user_id"]

        # 2. Duplicate registration rejected
        ok, msg, _ = auth_service.register_user("Test Citizen Real", unique_email, "securepass123", "securepass123")
        assert ok is False
        assert "already exists" in msg

        # 3. Wrong password rejected
        ok, msg, _ = auth_service.authenticate_user(unique_email, "wrongpassword")
        assert ok is False
        assert msg == "Incorrect email or password."

        # 4. Correct credentials succeed
        ok, msg, authed = auth_service.authenticate_user(unique_email, "securepass123")
        assert ok is True
        assert authed["user_id"] == user["user_id"]
        assert authed["name"] == "Test Citizen Real"




