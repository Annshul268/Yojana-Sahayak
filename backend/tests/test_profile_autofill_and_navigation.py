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


class TestSupabaseAuthAndDatabaseFlow:
    """Tests Supabase Auth, REST profile insertion, dynamic secrets, and DB auto-initialization."""

    def test_dynamic_secrets_resolution(self):
        from frontend.services.auth_service import get_env_or_secret

        with patch.dict("os.environ", {"SUPABASE_URL": "https://test.supabase.co"}):
            assert get_env_or_secret("SUPABASE_URL") == "https://test.supabase.co"

        with patch.dict("os.environ", {}, clear=True):
            with patch("streamlit.secrets", {"SUPABASE_URL": "https://secret.supabase.co"}):
                assert get_env_or_secret("SUPABASE_URL") == "https://secret.supabase.co"

        with patch.dict("os.environ", {}, clear=True):
            with patch("streamlit.secrets", {"supabase": {"url": "https://nested.supabase.co"}}):
                assert get_env_or_secret("SUPABASE_URL") == "https://nested.supabase.co"

    @patch("requests.post")
    def test_supabase_signup_success_with_profile_insert(self, mock_post):
        from frontend.services.auth_service import auth_service

        # Mock signup response
        signup_resp = MagicMock()
        signup_resp.status_code = 200
        signup_resp.json.return_value = {
            "user": {"id": "supabase-user-123", "email": "citizen@example.com"},
            "access_token": "mock-token-abc",
        }

        # Mock profile post response
        profile_resp = MagicMock()
        profile_resp.status_code = 201

        mock_post.side_effect = [signup_resp, profile_resp]

        def mock_secrets(key, default=""):
            if key == "SUPABASE_URL":
                return "https://mock.supabase.co"
            if key in ("SUPABASE_ANON_KEY", "SUPABASE_KEY"):
                return "mock-key"
            return default

        with patch("frontend.services.auth_service.get_env_or_secret", side_effect=mock_secrets):
            ok, msg, user = auth_service.register_user(
                "Pooja Verma", "citizen@example.com", "mypassword123", "mypassword123"
            )
            assert ok is True
            assert msg == "Account created successfully!"
            assert user["user_id"] == "supabase-user-123"
            assert user["name"] == "Pooja Verma"

        # Verify calls
        assert mock_post.call_count == 2
        # First call was signup
        signup_call = mock_post.call_args_list[0]
        assert "auth/v1/signup" in signup_call[0][0]
        # Second call was profile insert to REST
        prof_call = mock_post.call_args_list[1]
        assert "rest/v1/profiles" in prof_call[0][0]
        assert prof_call[1]["headers"]["Authorization"] == "Bearer mock-token-abc"

    @patch("requests.post")
    def test_supabase_signup_already_registered_error(self, mock_post):
        from frontend.services.auth_service import auth_service

        signup_resp = MagicMock()
        signup_resp.status_code = 400
        signup_resp.json.return_value = {"msg": "User already registered"}
        mock_post.return_value = signup_resp

        def mock_secrets(key, default=""):
            if key == "SUPABASE_URL":
                return "https://mock.supabase.co"
            if key in ("SUPABASE_ANON_KEY", "SUPABASE_KEY"):
                return "mock-key"
            return default

        with patch("frontend.services.auth_service.get_env_or_secret", side_effect=mock_secrets):
            ok, msg, user = auth_service.register_user(
                "Pooja Verma", "already@example.com", "mypassword123", "mypassword123"
            )
            assert ok is False
            assert "already exists" in msg

    @patch("requests.post")
    def test_supabase_signup_weak_password_error(self, mock_post):
        from frontend.services.auth_service import auth_service

        signup_resp = MagicMock()
        signup_resp.status_code = 422
        signup_resp.json.return_value = {"message": "Password should be at least 6 characters"}
        mock_post.return_value = signup_resp

        def mock_secrets(key, default=""):
            if key == "SUPABASE_URL":
                return "https://mock.supabase.co"
            if key in ("SUPABASE_ANON_KEY", "SUPABASE_KEY"):
                return "mock-key"
            return default

        with patch("frontend.services.auth_service.get_env_or_secret", side_effect=mock_secrets):
            ok, msg, user = auth_service.register_user(
                "Pooja Verma", "pooja@example.com", "weakpw", "weakpw"
            )
            assert ok is False
            assert "Password requirement" in msg or "Account creation failed" in msg

    @patch("requests.post")
    def test_supabase_signin_success(self, mock_post):
        from frontend.services.auth_service import auth_service

        signin_resp = MagicMock()
        signin_resp.status_code = 200
        signin_resp.json.return_value = {
            "user": {
                "id": "supabase-user-456",
                "email": "user@example.com",
                "user_metadata": {"name": "Rohan Sharma"},
            },
            "access_token": "token-123",
        }
        mock_post.return_value = signin_resp

        def mock_secrets(key, default=""):
            if key == "SUPABASE_URL":
                return "https://mock.supabase.co"
            if key in ("SUPABASE_ANON_KEY", "SUPABASE_KEY"):
                return "mock-key"
            return default

        with patch("frontend.services.auth_service.get_env_or_secret", side_effect=mock_secrets):
            ok, msg, authed = auth_service.authenticate_user("user@example.com", "mypassword123")
            assert ok is True
            assert msg == "Signed in successfully!"
            assert authed["user_id"] == "supabase-user-456"
            assert authed["name"] == "Rohan Sharma"

    @patch("requests.post")
    def test_supabase_signin_invalid_credentials(self, mock_post):
        from frontend.services.auth_service import auth_service

        signin_resp = MagicMock()
        signin_resp.status_code = 400
        signin_resp.json.return_value = {"error_description": "Invalid login credentials"}
        mock_post.return_value = signin_resp

        def mock_secrets(key, default=""):
            if key == "SUPABASE_URL":
                return "https://mock.supabase.co"
            if key in ("SUPABASE_ANON_KEY", "SUPABASE_KEY"):
                return "mock-key"
            return default

        with patch("frontend.services.auth_service.get_env_or_secret", side_effect=mock_secrets):
            ok, msg, _ = auth_service.authenticate_user("user@example.com", "wrongpassword")
            assert ok is False
            assert msg == "Incorrect email or password."

    def test_database_auto_creation_when_file_missing(self, tmp_path):
        from frontend.services.scheme_data import find_db_path, ensure_database_schema, upsert_user_profile_db, get_user_profile_db

        mock_db_file = str(tmp_path / "subdir" / "test_auto.db")
        # Ensure parent exists
        (tmp_path / "subdir").mkdir(parents=True, exist_ok=True)

        with patch.dict("os.environ", {"SQLITE_DB_PATH": mock_db_file}):
            # Before creation, file doesn't exist
            # find_db_path(create_if_missing=True) should create it
            path = find_db_path(create_if_missing=True)
            assert path == mock_db_file

            # ensure_database_schema creates tables
            assert ensure_database_schema(path) is True

            # Test upsert and get
            res = upsert_user_profile_db({"user_id": "test-uuid-99", "name": "Auto Citizen", "state": "Delhi"})
            assert res["ok"] is True

            prof = get_user_profile_db("test-uuid-99")
            assert prof is not None
            assert prof["name"] == "Auto Citizen"
            assert prof["state"] == "Delhi"


class TestPersonalEligibilityProfileBehavior:
    """Verifies that fresh accounts only populate Name, while all eligibility fields remain empty/unselected."""

    @patch("streamlit.rerun")
    @patch("streamlit.toast")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("streamlit.button")
    @patch("streamlit.text_input")
    @patch("streamlit.number_input")
    @patch("streamlit.selectbox")
    @patch("streamlit.radio")
    @patch("streamlit.checkbox")
    @patch("streamlit.form")
    @patch("streamlit.form_submit_button")
    @patch("frontend.services.api_client.api_client.get_profile")
    def test_fresh_signup_populates_only_name_and_all_other_fields_empty(
        self,
        mock_get_profile,
        mock_form_submit_btn,
        mock_form,
        mock_checkbox,
        mock_radio,
        mock_selectbox,
        mock_number_input,
        mock_text_input,
        mock_button,
        mock_markdown,
        mock_columns,
        mock_toast,
        mock_rerun,
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_form.return_value.__enter__ = MagicMock()
        mock_form.return_value.__exit__ = MagicMock()
        mock_form_submit_btn.return_value = False

        # Fresh user who just created an account with Full Name "Anshul Kumar Gupta"
        st.session_state.is_authenticated = True
        st.session_state.user_id = "user_fresh_123"
        st.session_state.user_name = "Anshul Kumar Gupta"

        # Database profile only has name and user_id, all eligibility fields are None/empty
        mock_get_profile.return_value = {
            "ok": True,
            "data": {
                "user_id": "user_fresh_123",
                "name": "Anshul Kumar Gupta",
                "state": "",
                "district": "",
                "age": None,
                "gender": "",
                "annual_income": None,
                "occupation": "",
                "category": "",
                "area": "",
                "disability": False,
            },
        }

        render_citizen_profile(MagicMock())

        # 1. Name is populated with signup name
        name_call = [c for c in mock_text_input.call_args_list if c[0][0] in ("Name", "नाम")][0]
        assert name_call[1]["value"] == "Anshul Kumar Gupta"

        # 2. District is empty
        district_call = [c for c in mock_text_input.call_args_list if c[0][0] in ("District", "जिला")][0]
        assert district_call[1]["value"] == ""

        # 3. Age is None (empty)
        age_call = [c for c in mock_number_input.call_args_list if c[0][0] in ("Age", "आयु")][0]
        assert age_call[1]["value"] is None

        # 4. Income is None (empty)
        inc_call = [c for c in mock_number_input.call_args_list if "Income" in c[0][0] or "आय" in c[0][0]][0]
        assert inc_call[1]["value"] is None

        # 5. Gender is unselected (index is None)
        gender_call = [c for c in mock_selectbox.call_args_list if c[0][0] in ("Gender", "लिंग")][0]
        assert gender_call[1]["index"] is None

        # 6. State is unselected (index is None)
        state_call = [c for c in mock_selectbox.call_args_list if "State" in c[0][0] or "राज्य" in c[0][0]][0]
        assert state_call[1]["index"] is None

        # 7. Occupation is unselected (index is None)
        occ_call = [c for c in mock_selectbox.call_args_list if "Occupation" in c[0][0] or "व्यवसाय" in c[0][0]][0]
        assert occ_call[1]["index"] is None

        # 8. Category is unselected (index is None)
        cat_call = [c for c in mock_selectbox.call_args_list if "Category" in c[0][0] or "श्रेणी" in c[0][0]][0]
        assert cat_call[1]["index"] is None

        # 9. Area radio is unselected (index is None)
        area_call = [c for c in mock_radio.call_args_list if "Area" in c[0][0] or "क्षेत्र" in c[0][0]][0]
        assert area_call[1]["index"] is None

        # 10. Disability is unchecked (False)
        dis_call = [c for c in mock_checkbox.call_args_list if "Disability" in c[0][0] or "दिव्यांगजन" in c[0][0]][0]
        assert dis_call[1]["value"] is False

    @patch("streamlit.rerun")
    @patch("streamlit.toast")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("streamlit.button")
    @patch("streamlit.text_input")
    @patch("streamlit.number_input")
    @patch("streamlit.selectbox")
    @patch("streamlit.radio")
    @patch("streamlit.checkbox")
    @patch("streamlit.form")
    @patch("streamlit.form_submit_button")
    @patch("frontend.services.api_client.api_client.get_profile")
    def test_saved_profile_loads_saved_eligibility_information(
        self,
        mock_get_profile,
        mock_form_submit_btn,
        mock_form,
        mock_checkbox,
        mock_radio,
        mock_selectbox,
        mock_number_input,
        mock_text_input,
        mock_button,
        mock_markdown,
        mock_columns,
        mock_toast,
        mock_rerun,
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_form.return_value.__enter__ = MagicMock()
        mock_form.return_value.__exit__ = MagicMock()
        mock_form_submit_btn.return_value = False

        st.session_state.is_authenticated = True
        st.session_state.user_id = "user_saved_456"
        st.session_state.user_name = "Test User"

        # User previously saved: Age=21, Gender=Male, State=Uttar Pradesh, Occupation=student, Income=150000, Area=Urban
        mock_get_profile.return_value = {
            "ok": True,
            "data": {
                "user_id": "user_saved_456",
                "name": "Test User",
                "state": "Uttar Pradesh",
                "district": "",
                "age": 21,
                "gender": "Male",
                "annual_income": 150000.0,
                "occupation": "student",
                "category": "OBC",
                "area": "Urban",
                "disability": False,
            },
        }

        render_citizen_profile(MagicMock())

        # Age is loaded
        age_call = [c for c in mock_number_input.call_args_list if c[0][0] in ("Age", "आयु")][0]
        assert age_call[1]["value"] == 21

        # Gender index for "Male"
        gender_call = [c for c in mock_selectbox.call_args_list if c[0][0] in ("Gender", "लिंग")][0]
        genders = gender_call[0][1]
        assert genders[gender_call[1]["index"]] == "Male"

        # State index for "Uttar Pradesh"
        state_call = [c for c in mock_selectbox.call_args_list if "State" in c[0][0] or "राज्य" in c[0][0]][0]
        states = state_call[0][1]
        assert states[state_call[1]["index"]] == "Uttar Pradesh"

        # Income is loaded
        inc_call = [c for c in mock_number_input.call_args_list if "Income" in c[0][0] or "आय" in c[0][0]][0]
        assert inc_call[1]["value"] == 150000.0

        # Area index for "Urban" is 1
        area_call = [c for c in mock_radio.call_args_list if "Area" in c[0][0] or "क्षेत्र" in c[0][0]][0]
        assert area_call[1]["index"] == 1

        # Field that was never entered (District) still remains empty
        district_call = [c for c in mock_text_input.call_args_list if c[0][0] in ("District", "जिला")][0]
        assert district_call[1]["value"] == ""

    @patch("streamlit.rerun")
    @patch("streamlit.toast")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("streamlit.button")
    @patch("frontend.services.api_client.api_client.get_profile")
    def test_sign_out_clears_session_state_and_user_isolation(
        self,
        mock_get_profile,
        mock_button,
        mock_markdown,
        mock_columns,
        mock_toast,
        mock_rerun,
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        # Simulate clicking Sign Out button
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "prof_signout_btn"

        st.session_state.is_authenticated = True
        st.session_state.user_id = "user_alice_789"
        st.session_state.user_name = "Alice"
        st.session_state.eligibility_answers = {"age": 30, "state": "Bihar"}
        st.session_state.field_age = 30

        render_citizen_profile(MagicMock())

        assert st.session_state.is_authenticated is False
        assert st.session_state.user_id == ""
        assert st.session_state.user_name is None
        assert "eligibility_answers" not in st.session_state
        assert "field_age" not in st.session_state


class TestProfileSaveNavigationRouting:
    """Verifies that 'Save Profile' routes to Home when opened normally,
    and returns to the specific Auto Fill questionnaire flow when opened from Auto Fill."""

    def setup_method(self):
        st.session_state.clear()
        st.session_state.is_authenticated = True
        st.session_state.user_id = "user_nav_test"
        st.session_state.user_name = "Test Citizen"

    @patch("streamlit.rerun")
    @patch("streamlit.toast")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("streamlit.button")
    @patch("streamlit.text_input")
    @patch("streamlit.number_input")
    @patch("streamlit.selectbox")
    @patch("streamlit.radio")
    @patch("streamlit.checkbox")
    @patch("streamlit.form")
    @patch("streamlit.form_submit_button")
    @patch("frontend.services.api_client.api_client.get_profile")
    @patch("frontend.services.api_client.api_client.upsert_profile")
    def test_save_profile_from_home_navigates_to_home(
        self,
        mock_upsert_profile,
        mock_get_profile,
        mock_form_submit_btn,
        mock_form,
        mock_checkbox,
        mock_radio,
        mock_selectbox,
        mock_number_input,
        mock_text_input,
        mock_button,
        mock_markdown,
        mock_columns,
        mock_toast,
        mock_rerun,
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_form.return_value.__enter__ = MagicMock()
        mock_form.return_value.__exit__ = MagicMock()
        mock_button.return_value = False
        mock_form_submit_btn.return_value = True  # User clicks "Save Profile"
        mock_get_profile.return_value = {"ok": True, "data": {"user_id": "user_nav_test", "name": "Test Citizen"}}
        mock_upsert_profile.return_value = {"ok": True}

        # Case 1: Normal opening from Home -> Citizen Profile (no autofill return context)
        assert "profile_return_context" not in st.session_state
        assert "auth_return_page" not in st.session_state

        mock_text_input.side_effect = lambda label, *args, **kwargs: "Test Citizen" if "Name" in label or "नाम" in label else ""
        mock_number_input.side_effect = lambda label, *args, **kwargs: 25 if "Age" in label or "आयु" in label else 200000.0
        mock_selectbox.side_effect = lambda label, *args, **kwargs: "Delhi" if "State" in label or "राज्य" in label else ("Male" if "Gender" in label or "लिंग" in label else "student")
        mock_radio.side_effect = lambda label, *args, **kwargs: "Urban"
        mock_checkbox.side_effect = lambda label, *args, **kwargs: False

        mock_navigate = MagicMock()
        render_citizen_profile(mock_navigate)

        # Upsert profile was called
        mock_upsert_profile.assert_called_once()
        # Navigated to home
        mock_navigate.assert_called_once_with("home")
        # Did NOT call rerun
        mock_rerun.assert_not_called()

    @patch("streamlit.rerun")
    @patch("streamlit.toast")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("streamlit.button")
    @patch("streamlit.text_input")
    @patch("streamlit.number_input")
    @patch("streamlit.selectbox")
    @patch("streamlit.radio")
    @patch("streamlit.checkbox")
    @patch("streamlit.form")
    @patch("streamlit.form_submit_button")
    @patch("frontend.services.api_client.api_client.get_profile")
    @patch("frontend.services.api_client.api_client.upsert_profile")
    def test_save_profile_from_autofill_returns_to_finder(
        self,
        mock_upsert_profile,
        mock_get_profile,
        mock_form_submit_btn,
        mock_form,
        mock_checkbox,
        mock_radio,
        mock_selectbox,
        mock_number_input,
        mock_text_input,
        mock_button,
        mock_markdown,
        mock_columns,
        mock_toast,
        mock_rerun,
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_form.return_value.__enter__ = MagicMock()
        mock_form.return_value.__exit__ = MagicMock()
        mock_button.return_value = False
        mock_form_submit_btn.return_value = True  # User clicks "Save Profile"
        mock_get_profile.return_value = {"ok": True, "data": {"user_id": "user_nav_test", "name": "Test Citizen"}}
        mock_upsert_profile.return_value = {"ok": True}

        # Case 2: Opened from Auto Fill questionnaire
        st.session_state.profile_return_context = {
            "source": "eligibility_autofill",
            "target_page": "finder",
            "intent": "agriculture",
            "questionnaire_step": 2,
            "mode": "autofill",
            "answers": {"state": "Punjab"},
        }

        mock_text_input.side_effect = lambda label, *args, **kwargs: "Test Citizen" if "Name" in label or "नाम" in label else ""
        mock_number_input.side_effect = lambda label, *args, **kwargs: 35 if "Age" in label or "आयु" in label else 150000.0
        mock_selectbox.side_effect = lambda label, *args, **kwargs: "Punjab" if "State" in label or "राज्य" in label else ("Male" if "Gender" in label or "लिंग" in label else "farmer")
        mock_radio.side_effect = lambda label, *args, **kwargs: "Rural"
        mock_checkbox.side_effect = lambda label, *args, **kwargs: False

        mock_navigate = MagicMock()
        render_citizen_profile(mock_navigate)

        # Upsert profile was called
        mock_upsert_profile.assert_called_once()
        # Must return to "finder" (NOT home)
        mock_navigate.assert_called_once_with("finder")
        # Context must be cleared to prevent stale navigation
        assert "profile_return_context" not in st.session_state
        # Fill mode set to autofill and intent restored
        assert st.session_state.get("fill_mode") == "autofill"
        assert st.session_state.get("questionnaire_step") == 2
        assert st.session_state["eligibility_answers"].get("intent") == "agriculture"
        assert st.session_state["eligibility_answers"].get("state") == "Punjab"
        assert st.session_state["eligibility_answers"].get("age") == 35

    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("frontend.services.api_client.api_client.get_profile")
    def test_back_from_autofill_returns_to_finder_without_saving(
        self,
        mock_get_profile,
        mock_markdown,
        mock_columns,
        mock_button,
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_get_profile.return_value = {"ok": True, "data": {"user_id": "user_nav_test", "name": "Test Citizen"}}

        # User clicked back button
        mock_button.side_effect = lambda *args, **kwargs: kwargs.get("key") == "profile_back_btn"

        st.session_state.profile_return_context = {
            "source": "eligibility_autofill",
            "target_page": "finder",
            "intent": "education",
            "questionnaire_step": 1,
            "mode": "autofill",
            "answers": {},
        }

        mock_navigate = MagicMock()
        render_citizen_profile(mock_navigate)

        # Returned to finder
        mock_navigate.assert_called_once_with("finder")
        # Intent preserved in pending_category_intent
        assert st.session_state.get("pending_category_intent") == "education"
        # Context cleared
        assert "profile_return_context" not in st.session_state

    @patch("streamlit.rerun")
    @patch("streamlit.toast")
    @patch("streamlit.columns")
    @patch("streamlit.markdown")
    @patch("streamlit.button")
    @patch("streamlit.text_input")
    @patch("streamlit.number_input")
    @patch("streamlit.selectbox")
    @patch("streamlit.radio")
    @patch("streamlit.checkbox")
    @patch("streamlit.form")
    @patch("streamlit.form_submit_button")
    @patch("frontend.services.api_client.api_client.get_profile")
    @patch("frontend.services.api_client.api_client.upsert_profile")
    def test_subsequent_profile_save_navigates_to_home_after_autofill_cleared(
        self,
        mock_upsert_profile,
        mock_get_profile,
        mock_form_submit_btn,
        mock_form,
        mock_checkbox,
        mock_radio,
        mock_selectbox,
        mock_number_input,
        mock_text_input,
        mock_button,
        mock_markdown,
        mock_columns,
        mock_toast,
        mock_rerun,
    ):
        mock_columns.side_effect = lambda spec, *args, **kwargs: [
            MagicMock() for _ in range(len(spec) if isinstance(spec, (list, tuple)) else int(spec))
        ]
        mock_form.return_value.__enter__ = MagicMock()
        mock_form.return_value.__exit__ = MagicMock()
        mock_button.return_value = False
        mock_form_submit_btn.return_value = True
        mock_get_profile.return_value = {"ok": True, "data": {"user_id": "user_nav_test", "name": "Test Citizen"}}
        mock_upsert_profile.return_value = {"ok": True}

        # Clear any prior context
        st.session_state.pop("profile_return_context", None)
        st.session_state.pop("auth_return_page", None)

        mock_navigate = MagicMock()
        render_citizen_profile(mock_navigate)

        mock_navigate.assert_called_once_with("home")





