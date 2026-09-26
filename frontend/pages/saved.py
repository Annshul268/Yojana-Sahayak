"""Minimal Saved Schemes bookmark view."""

from typing import Callable
import streamlit as st
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language, t


def render_saved_schemes(navigate_to: Callable[[str], None]) -> None:
    lang = get_current_language()
    user_id = st.session_state.get("user_id", "citizen_user_1")

    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="color: #1E3A8A; font-weight: 700; margin-bottom: 4px;">
                {"सहेजी गई योजनाएं" if lang == "hi" else "Saved Schemes"}
            </h2>
            <p style="color: #6B7280; font-size: 0.95rem;">
                {"आपकी बुकमार्क की गई योजनाएं यहां सुरक्षित हैं।" if lang == "hi" else "Your bookmarked welfare schemes appear here for quick access."}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    res = api_client.list_saved(user_id=user_id)
    if not res["ok"]:
        st.error("Unable to load saved schemes right now.")
        return

    saved_items = res["data"]
    if not saved_items:
        st.markdown(
            f"""
            <div style="background: white; border: 1px dashed #D1D5DB; border-radius: 8px; padding: 2.5rem 1.5rem; text-align: center; margin: 2rem 0;">
                <div style="font-size: 2rem; margin-bottom: 8px;">⭐</div>
                <h4 style="color: #374151; margin-bottom: 6px;">{"अभी तक कोई योजना सहेजी नहीं गई है।" if lang == "hi" else "No saved schemes yet."}</h4>
                <p style="color: #6B7280; font-size: 0.9rem; max-width: 420px; margin: 0 auto 16px auto;">
                    {"योजनाएं ब्राउज़ करते समय उन्हें बाद में आसानी से खोजने के लिए 'Save' बटन पर क्लिक करें।" if lang == "hi" else "Save schemes while browsing to find them here later."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📚 " + ("योजनाएं देखें" if lang == "hi" else "Browse Schemes"), type="primary"):
            navigate_to("schemes")
        return

    for item in saved_items:
        scheme = item.get("scheme")
        if not scheme:
            continue

        name = scheme.get("name_hi") if (lang == "hi" and scheme.get("name_hi")) else scheme.get("name", "")
        slug = scheme.get("slug", "")
        scheme_id = scheme.get("id", "")
        category = scheme.get("category", "")
        official_url = scheme.get("official_url", "#")

        with st.container():
            st.markdown(
                f"""
                <div class="clean-card" style="margin-bottom: 12px; padding: 1.25rem;">
                    <span class="category-chip">{category}</span>
                    <h3 style="color: #1E3A8A; margin: 6px 0 10px 0; font-size: 1.15rem; font-weight: 700;">
                        {name}
                    </h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col1, col2, col3 = st.columns([4, 2, 4])
            with col1:
                if st.button("View Scheme", key=f"saved_view_{slug}", type="primary", use_container_width=True):
                    st.session_state.selected_scheme_slug = slug
                    st.session_state["_scheme_scroll_to_top"] = True
                    navigate_to("scheme_details")
            with col2:
                if st.button("Remove 🗑️", key=f"saved_rem_{slug}", use_container_width=True):
                    api_client.remove_saved_scheme(scheme_id=scheme_id, user_id=user_id)
                    st.toast("Removed from bookmarks")
                    st.rerun()
            with col3:
                st.link_button("Official Website 🔗", official_url, use_container_width=True)

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
