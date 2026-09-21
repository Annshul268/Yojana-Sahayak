"""Top navigation and branding banner with language switch."""

import streamlit as st
from frontend.utils.i18n import get_current_language, t


def render_navbar() -> None:
    """Renders the top civic navigation banner with language toggle."""
    col1, col2, col3 = st.columns([5, 2, 2])

    with col1:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 5px;">
                <span style="font-size: 32px;">🏛️</span>
                <div>
                    <h2 style="margin: 0; color: #1A365D; font-weight: 800; font-size: 1.7rem; letter-spacing: -0.5px;">
                        {t('app_title', 'योजना सहायक')}
                    </h2>
                    <p style="margin: 0; color: #718096; font-size: 0.88rem; font-weight: 500;">
                        {t('app_subtitle', 'AI Government Scheme & Benefits Navigator')}
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        # Language Selector
        current_lang = get_current_language()
        lang_choice = st.selectbox(
            "🌐 भाषा / Language",
            options=["English", "हिन्दी (Hindi)"],
            index=0 if current_lang == "en" else 1,
            key="lang_selector",
            label_visibility="collapsed",
        )
        new_lang = "en" if "English" in lang_choice else "hi"
        if new_lang != current_lang:
            st.session_state.lang = new_lang
            st.rerun()

    with col3:
        # User Profile Status Pill
        user_name = st.session_state.get("user_name", "Citizen Guest")
        st.markdown(
            f"""
            <div style="text-align: right; padding-top: 5px;">
                <span style="background-color: #EDF2F7; color: #2D3748; padding: 6px 12px; border-radius: 16px; font-size: 0.82rem; font-weight: 600; border: 1px solid #CBD5E0;">
                    👤 {user_name}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='margin: 8px 0 16px 0; border: none; border-top: 2px solid #E2E8F0;' />", unsafe_allow_html=True)
