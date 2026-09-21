"""Saved Schemes bookmark manager view."""

from typing import Callable
import streamlit as st
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language, t


def render_saved_schemes(navigate_to: Callable[[str], None]) -> None:
    st.markdown("## ⭐ " + t("nav_saved", "Saved Schemes"))
    st.caption("Access and manage your bookmarked government schemes.")

    user_id = st.session_state.get("user_id", "guest_user_1")
    lang = get_current_language()

    with st.spinner("Loading bookmarked schemes..."):
        res = api_client.list_saved(user_id=user_id)

    if not res["ok"]:
        st.error(f"Error loading saved schemes: {res['error']}")
        return

    saved_items = res["data"]
    if not saved_items:
        st.info("You haven't bookmarked any schemes yet.")
        if st.button("📚 Explore Schemes Directory", type="primary"):
            navigate_to("schemes")
        return

    st.markdown(f"**You have {len(saved_items)} saved schemes**")
    st.markdown("<hr style='margin: 8px 0 16px 0; border: none; border-top: 1px solid #E2E8F0;' />", unsafe_allow_html=True)

    for item in saved_items:
        scheme = item.get("scheme")
        if not scheme:
            continue

        name = scheme.get("name_hi") if (lang == "hi" and scheme.get("name_hi")) else scheme.get("name", "")
        desc = scheme.get("description_hi") if (lang == "hi" and scheme.get("description_hi")) else scheme.get("description", "")
        slug = scheme.get("slug", "")
        scheme_id = scheme.get("id", "")
        official_url = scheme.get("official_url", "#")

        with st.container():
            st.markdown(
                f"""
                <div style="background: white; border: 1px solid #CBD5E0; border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem;">
                    <span style="background: #EDF2F7; color: #4A5568; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">{scheme.get('category')}</span>
                    <h4 style="margin: 6px 0; color: #1A365D;">{name}</h4>
                    <p style="color: #4A5568; font-size: 0.9rem; line-height: 1.5; margin-bottom: 8px;">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col1, col2, col3, col_space = st.columns([2, 2, 3, 3])
            with col1:
                if st.button("📋 Details", key=f"saved_det_{slug}", use_container_width=True):
                    st.session_state.selected_scheme_slug = slug
                    navigate_to("scheme_details")
            with col2:
                if st.button("🗑️ Remove", key=f"saved_rem_{slug}", use_container_width=True):
                    api_client.remove_saved_scheme(scheme_id=scheme_id, user_id=user_id)
                    st.toast("Scheme removed from bookmarks")
                    st.rerun()
            with col3:
                st.link_button("🔗 Official Portal", official_url, use_container_width=True)
