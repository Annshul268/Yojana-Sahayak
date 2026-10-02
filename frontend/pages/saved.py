"""Minimal Saved Schemes bookmark view."""

from typing import Callable
import streamlit as st
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language, t


def render_saved_schemes(navigate_to: Callable[[str], None]) -> None:
    lang = get_current_language()
    is_authenticated = bool(st.session_state.get("is_authenticated", False))
    user_id = st.session_state.get("user_id", "")

    # Back Link button
    back_label = "← " + ("पीछे" if lang == "hi" else "Back")

    def on_saved_back():
        last_page = st.session_state.get("_last_rendered_page")
        if last_page and last_page not in ("saved", "scheme_details", "admin"):
            navigate_to(last_page)
        else:
            navigate_to("home")

    if st.button(back_label, key="saved_back_btn", on_click=on_saved_back):
        on_saved_back()

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

    if not is_authenticated or not user_id:
        st.markdown(
            f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 2.5rem 1.5rem; text-align: center; max-width: 580px; margin: 2rem auto;">
                <div style="font-size: 2.2rem; margin-bottom: 10px;">⭐</div>
                <h3 style="color: #0F172A; font-weight: 700; margin-bottom: 8px;">
                    {"सहेजी गई योजनाएं देखने के लिए साइन इन करें" if lang == "hi" else "Sign in to view Saved Schemes"}
                </h3>
                <p style="color: #64748B; font-size: 0.95rem; line-height: 1.6; margin-bottom: 20px;">
                    {"अपनी बुकमार्क की गई योजनाओं को किसी भी डिवाइस से सुरक्षित रूप से एक्सेस करने के लिए साइन इन करें।" if lang == "hi" else "Sign in to access your bookmarked schemes and manage them securely across devices."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
        with col_c2:
            def on_go_to_signin_saved():
                st.session_state["auth_redirect_target"] = "saved"
                navigate_to("profile")

            st.button(
                "खाते में साइन इन करें" if lang == "hi" else "Sign In to Your Account",
                type="primary",
                use_container_width=True,
                key="saved_signin_btn",
                on_click=on_go_to_signin_saved,
            )
        return

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
        st.button("📚 " + ("योजनाएं देखें" if lang == "hi" else "Browse Schemes"), type="primary", on_click=navigate_to, args=("schemes",))
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

            st.markdown("<div class='saved-card-actions'>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([4, 2, 4])
            with col1:
                def on_saved_view(s_slug=slug):
                    st.session_state.selected_scheme_slug = s_slug
                    st.session_state["scheme_navigation_source"] = "saved"
                    st.session_state["_scheme_scroll_to_top"] = True
                    navigate_to("scheme_details")

                st.button("View Scheme", key=f"saved_view_{slug}", type="primary", use_container_width=True, on_click=on_saved_view, args=(slug,))
            with col2:
                if st.button("Remove", key=f"saved_rem_{slug}", use_container_width=True):
                    api_client.remove_saved_scheme(scheme_id=scheme_id, user_id=user_id)
                    st.toast("Removed from bookmarks")
                    st.rerun()
            with col3:
                st.link_button("Official Website 🔗", official_url, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
