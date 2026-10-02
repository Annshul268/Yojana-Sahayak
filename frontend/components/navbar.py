"""Top navigation bar matching Lovable civic design system."""

from typing import Callable, Optional
import streamlit as st
from frontend.utils.i18n import get_current_language, t


def render_navbar(navigate_to: Optional[Callable[[str], None]] = None) -> None:
    """Renders a sleek top bar: Logo | Home | Check eligibility | All schemes | Language | Sign in."""
    lang = get_current_language()
    cur_page = st.session_state.get("current_page", "home")

    # 1. Desktop Navigation Bar (visible on desktop >= 769px)
    with st.container(key="desktop_nav_wrapper"):
        col_brand, col_home, col_apps, col_lang, col_auth = st.columns(
            [4.1, 1.1, 1.8, 0.65, 1.35],
            gap="small",
            vertical_alignment="center",
        )

        with col_brand:
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
            def on_nav_home():
                if navigate_to:
                    navigate_to("home")

            st.button(
                label,
                key="nav_home_btn",
                type="primary" if is_active else "secondary",
                use_container_width=True,
                on_click=on_nav_home,
            )

        with col_apps:
            is_active = (cur_page in ("tracker", "applications"))
            label = "मेरे आवेदन" if lang == "hi" else "My Applications"
            def on_nav_apps():
                if not st.session_state.get("is_authenticated", False):
                    st.session_state.auth_redirect_target = "tracker"
                    if navigate_to:
                        navigate_to("profile")
                else:
                    if navigate_to:
                        navigate_to("tracker")

            st.button(
                label,
                key="nav_apps_btn",
                type="primary" if is_active else "secondary",
                use_container_width=True,
                on_click=on_nav_apps,
            )

        with col_lang:
            st.markdown("<div class='nav-globe-wrapper'>", unsafe_allow_html=True)
            help_text = "Change language"
            def on_lang_toggle():
                st.session_state.lang = "hi" if lang == "en" else "en"

            st.button(
                "",
                key="nav_lang_toggle_btn",
                icon=":material/language:",
                help=help_text,
                use_container_width=True,
                on_click=on_lang_toggle,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col_auth:
            user_name = st.session_state.get("user_name")
            is_logged_in = bool(st.session_state.get("is_authenticated", False))
            auth_label = user_name[:8] if (is_logged_in and user_name) else ("साइन इन" if lang == "hi" else "Sign in")
            btn_type = "primary" if not is_logged_in else "secondary"
            def on_nav_auth():
                if navigate_to:
                    navigate_to("profile")

            st.button(
                auth_label,
                key="nav_auth_btn",
                type=btn_type,
                use_container_width=True,
                on_click=on_nav_auth,
            )

    # 2. Mobile Navigation Bar (visible on screens <= 768px)
    # Order: [ ☰ MENU ] [ YS LOGO + NAME ] [ FLEXIBLE SPACE ] [ LANGUAGE ] [ SIGN IN ]
    with st.container(key="mobile_nav_wrapper"):
        col_m_menu, col_m_logo, col_m_lang, col_m_auth = st.columns(
            [1.0, 5.0, 1.0, 1.8],
            gap="small",
            vertical_alignment="center",
        )

        with col_m_menu:
            with st.popover("☰", use_container_width=True):
                st.markdown(
                    f"<div style='font-size: 0.8rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 6px;'>{'नेविगेशन' if lang == 'hi' else 'Navigation'}</div>",
                    unsafe_allow_html=True,
                )
                # 1. Home
                if st.button("होम" if lang == "hi" else "Home", key="mob_menu_home", use_container_width=True, type="primary" if cur_page == "home" else "secondary"):
                    if navigate_to:
                        navigate_to("home")
                # 2. Check Eligibility
                if st.button("पात्रता जांचें" if lang == "hi" else "Check Eligibility", key="mob_menu_finder", use_container_width=True, type="primary" if cur_page == "finder" else "secondary"):
                    from frontend.pages.scheme_finder import reset_eligibility_session
                    reset_eligibility_session()
                    if navigate_to:
                        navigate_to("finder")
                # 3. Browse Schemes
                if st.button("सभी योजनाएं" if lang == "hi" else "Browse Schemes", key="mob_menu_schemes", use_container_width=True, type="primary" if cur_page in ("schemes", "all_schemes") else "secondary"):
                    if navigate_to:
                        navigate_to("schemes")
                # 4. Saved Schemes
                if st.button("सहेजी गई योजनाएं" if lang == "hi" else "Saved Schemes", key="mob_menu_saved", use_container_width=True, type="primary" if cur_page in ("saved", "saved_schemes") else "secondary"):
                    if navigate_to:
                        navigate_to("saved")
                # 5. My Applications
                if st.button("मेरे आवेदन" if lang == "hi" else "My Applications", key="mob_menu_apps", use_container_width=True, type="primary" if cur_page in ("tracker", "applications", "my_applications") else "secondary"):
                    if not is_logged_in:
                        st.session_state.auth_redirect_target = "tracker"
                        if navigate_to:
                            navigate_to("profile")
                    else:
                        if navigate_to:
                            navigate_to("tracker")
                # 6. Citizen Profile / Sign In
                st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 8px 0;' />", unsafe_allow_html=True)
                prof_label = user_name if (is_logged_in and user_name) else ("साइन इन" if lang == "hi" else "Citizen Profile / Sign In")
                if st.button(prof_label, key="mob_menu_profile", use_container_width=True, type="primary" if cur_page == "profile" else "secondary"):
                    if navigate_to:
                        navigate_to("profile")

        with col_m_logo:
            st.markdown(
                """
                <div class="mob-brand-box" style="display: flex; align-items: center; gap: 7px; cursor: pointer;">
                    <span class="mob-logo-badge" style="display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; background: #1E3A8A; color: white; border-radius: 7px; font-size: 13px; font-weight: 800; flex-shrink: 0;">
                        YS
                    </span>
                    <span class="mob-logo-title" style="font-size: 1.02rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em; white-space: nowrap;">
                        Yojana Sahayak
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_m_lang:
            st.markdown("<div class='nav-globe-wrapper'>", unsafe_allow_html=True)
            st.button(
                "",
                key="mob_nav_lang_btn",
                icon=":material/language:",
                help="Change language",
                use_container_width=True,
                on_click=on_lang_toggle,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col_m_auth:
            st.button(
                auth_label,
                key="mob_nav_auth_btn",
                type=btn_type,
                use_container_width=True,
                on_click=on_nav_auth,
            )

    st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 0.5rem 0 1rem 0;' />", unsafe_allow_html=True)
