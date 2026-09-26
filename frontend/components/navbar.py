"""Top navigation bar matching Lovable civic design system."""

from typing import Callable, Optional
import streamlit as st
from frontend.utils.i18n import get_current_language, t


def render_navbar(navigate_to: Optional[Callable[[str], None]] = None) -> None:
    """Renders a sleek top bar: Logo | Home | Check eligibility | All schemes | Language | Sign in."""
    lang = get_current_language()
    cur_page = st.session_state.get("current_page", "home")

    # Single-line header columns: Logo | Home | My Applications | Language | Profile
    col_brand, col_home, col_apps, col_lang, col_auth = st.columns(
        [4.0, 1.1, 1.7, 0.8, 1.3],
        gap="small",
        vertical_alignment="center",
    )

    with col_brand:
        # Logo with shield icon
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                <span style="display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; background: #1E3A8A; color: white; border-radius: 8px; font-size: 14px; font-weight: 800;">
                    YS
                </span>
                <span style="font-size: 1.2rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">
                    Yojana Sahayak
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_home:
        is_active = (cur_page == "home")
        label = "होम" if lang == "hi" else "Home"
        if st.button(
            label,
            key="nav_home_btn",
            type="primary" if is_active else "secondary",
            use_container_width=True,
        ):
            if navigate_to:
                navigate_to("home")

    with col_apps:
        is_active = (cur_page in ("tracker", "applications"))
        label = "मेरे आवेदन" if lang == "hi" else "My Applications"
        if st.button(
            label,
            key="nav_apps_btn",
            type="primary" if is_active else "secondary",
            use_container_width=True,
        ):
            if not st.session_state.get("is_authenticated", False):
                st.session_state.auth_redirect_target = "tracker"
                if navigate_to:
                    navigate_to("profile")
            else:
                if navigate_to:
                    navigate_to("tracker")

    with col_lang:
        # Language Switcher Pill [ EN | हि ]
        pill_label = "हि" if lang == "en" else "EN"
        btn_label = pill_label
        help_text = "हिंदी में बदलें" if lang == "en" else "Switch to English"
        if st.button(btn_label, key="nav_lang_toggle_btn", help=help_text, use_container_width=True):
            st.session_state.lang = "hi" if lang == "en" else "en"
            st.rerun()

    with col_auth:
        user_name = st.session_state.get("user_name")
        is_logged_in = bool(st.session_state.get("is_authenticated", False))
        auth_label = user_name[:8] if (is_logged_in and user_name) else ("साइन इन" if lang == "hi" else "Sign in")
        btn_type = "primary" if not is_logged_in else "secondary"
        if st.button(auth_label, key="nav_auth_btn", type=btn_type, use_container_width=True):
            if navigate_to:
                navigate_to("profile")

    st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 0.5rem 0 1rem 0;' />", unsafe_allow_html=True)
