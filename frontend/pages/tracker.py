"""My Applications - Clean Row-Based Application Tracking View."""

from typing import Any, Callable, Dict, List, Optional
import streamlit as st
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language

APPLICATION_STATUSES = [
    "Saved",
    "Planning to Apply",
    "Applied",
    "Application Submitted",
    "Completed",
]


def render_application_tracker(navigate_to: Callable[[str], None]) -> None:
    """Renders the simple row-based 'My Applications' page."""
    lang = get_current_language()
    is_authenticated = bool(st.session_state.get("is_authenticated", False))
    user_id = st.session_state.get("user_id", "")
    user_name = st.session_state.get("user_name", "Citizen")

    # Back Link button
    back_label = "← " + ("पीछे" if lang == "hi" else "Back")

    def on_tracker_back():
        last_page = st.session_state.get("_last_rendered_page")
        if last_page and last_page not in ("tracker", "applications", "scheme_details", "admin"):
            navigate_to(last_page)
        else:
            navigate_to("home")

    if st.button(back_label, key="tracker_back_btn", on_click=on_tracker_back):
        on_tracker_back()

    # Header
    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="color: #0F172A; font-size: 2.1rem; font-weight: 800; margin: 0 0 6px 0; letter-spacing: -0.02em;">
                {"मेरे आवेदन" if lang == "hi" else "My Applications"}
            </h1>
            <p style="color: #475569; font-size: 1rem; margin: 0; line-height: 1.5;">
                {"आवेदन के लिए आपके द्वारा जोड़ी गई सरकारी योजनाओं को ट्रैक करें" if lang == "hi" else "Track the government schemes you've added for application"}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Unauthenticated Guard
    if not is_authenticated or not user_id:
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 2rem; text-align: center; max-width: 580px; margin: 2rem auto;">
                <h3 style="color: #0F172A; font-weight: 700; margin-bottom: 8px;">
                    {"अपने आवेदन देखने के लिए साइन इन करें" if lang == "hi" else "Sign in to view My Applications"}
                </h3>
                <p style="color: #64748B; font-size: 0.95rem; line-height: 1.6; margin-bottom: 20px;">
                    {"अपने आवेदनों को ट्रैक और प्रबंधित करने के लिए कृपया साइन इन करें।" if lang == "hi" else "Please sign in to track and manage your applications."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
        with col_c2:
            def on_go_to_signin_tracker():
                st.session_state["auth_redirect_target"] = "tracker"
                navigate_to("profile")

            st.button(
                "खाते में साइन इन करें" if lang == "hi" else "Sign In to Your Account",
                type="primary",
                use_container_width=True,
                key="tracker_signin_btn",
                on_click=on_go_to_signin_tracker,
            )
        return

    # 2. Retrieve Applications
    res = api_client.list_tracking(user_id=user_id)
    entries = res.get("data", []) if res.get("ok") else []

    # 3. Empty State
    if not entries:
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 12px; padding: 3rem 2rem; text-align: center; margin: 1.5rem 0;">
                <h3 style="color: #0F172A; font-weight: 700; margin-bottom: 8px;">
                    {"अभी तक कोई आवेदन नहीं" if lang == "hi" else "No applications yet"}
                </h3>
                <p style="color: #64748B; font-size: 0.98rem; max-width: 480px; margin: 0 auto 20px auto; line-height: 1.6;">
                    {"उन सरकारी लाभों पर नज़र रखने के लिए यहाँ योजनाएं जोड़ें जिनके लिए आप आवेदन करने की योजना बना रहे हैं।" if lang == "hi" else "Add schemes to My Applications to keep track of them here."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_emp1, col_emp2, col_emp3 = st.columns([1.5, 2, 1.5])
        with col_emp2:
            browse_label = "सभी योजनाएं ब्राउज़ करें" if lang == "hi" else "Browse All Schemes"
            st.button(browse_label, type="primary", use_container_width=True, key="empty_browse_btn", on_click=navigate_to, args=("schemes",))
        return

    # 4. Simple Row-Based List (Status | Scheme Name | Official Link | Remove)
    st.markdown("<div class='applications-table'>", unsafe_allow_html=True)

    # Table Header (desktop table header, hidden on mobile)
    st.markdown("<div class='app-table-header-row'>", unsafe_allow_html=True)
    col_h_status, col_h_name, col_h_link, col_h_remove = st.columns(
        [2.2, 5.0, 1.6, 1.2],
        gap="medium",
        vertical_alignment="center",
    )
    with col_h_status:
        st.markdown(
            f"<div class='app-table-header'>{'स्थिति' if lang == 'hi' else 'Status'}</div>",
            unsafe_allow_html=True,
        )
    with col_h_name:
        st.markdown(
            f"<div class='app-table-header'>{'योजना का नाम' if lang == 'hi' else 'Scheme Name'}</div>",
            unsafe_allow_html=True,
        )
    with col_h_link:
        st.markdown(
            f"<div class='app-table-header'>{'आधिकारिक लिंक' if lang == 'hi' else 'Official Link'}</div>",
            unsafe_allow_html=True,
        )
    with col_h_remove:
        st.markdown(
            f"<div class='app-table-header'>{'हटाएं' if lang == 'hi' else 'Remove'}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border: none; border-top: 1px solid #CBD5E1; margin: 8px 0 12px 0;' />", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Application Rows
    for idx, entry in enumerate(entries):
        tracking_id = entry.get("id")
        current_status = entry.get("status", "Saved")
        scheme = entry.get("scheme") or {}
        scheme_name = (
            scheme.get("name_hi")
            if (lang == "hi" and scheme.get("name_hi"))
            else scheme.get("name", "Unknown Scheme")
        )
        slug = scheme.get("slug", "")
        official_url = scheme.get("official_url") or "#"

        st.markdown(f"<div class='app-table-row' id='app-row-{tracking_id}'>", unsafe_allow_html=True)
        col_status, col_name, col_link, col_remove = st.columns(
            [2.2, 5.0, 1.6, 1.2],
            gap="medium",
            vertical_alignment="center",
        )

        with col_status:
            # Preserve existing status options
            status_options = APPLICATION_STATUSES[:]
            if current_status not in status_options:
                status_options.append(current_status)

            cur_idx = status_options.index(current_status)
            new_status = st.selectbox(
                "Status",
                status_options,
                index=cur_idx,
                key=f"status_row_{tracking_id}",
                label_visibility="collapsed",
            )
            if new_status != current_status:
                api_client.update_tracking(
                    tracking_id=tracking_id,
                    user_id=user_id,
                    status=new_status,
                )
                st.toast(f"Status updated to: {new_status}")
                st.rerun()

        with col_name:
            def on_tracker_view(s_slug=slug):
                st.session_state.selected_scheme_slug = s_slug
                st.session_state["scheme_navigation_source"] = "applications"
                st.session_state["_scheme_scroll_to_top"] = True
                navigate_to("scheme_details")

            st.button(
                scheme_name,
                key=f"scheme_name_{tracking_id}",
                use_container_width=True,
                help="View Scheme",
                on_click=on_tracker_view,
                args=(slug,),
            )

        with col_link:
            if official_url and official_url.startswith("http"):
                st.link_button(
                    "Official Link" if lang != "hi" else "आधिकारिक लिंक",
                    official_url,
                    use_container_width=True,
                )
            else:
                st.button("Official Link", disabled=True, use_container_width=True, key=f"no_link_{tracking_id}")

        with col_remove:
            remove_label = "हटाएं" if lang == "hi" else "Remove"
            if st.button(
                remove_label,
                key=f"remove_row_{tracking_id}",
                type="secondary",
                use_container_width=True,
            ):
                api_client.delete_tracking(tracking_id=tracking_id, user_id=user_id)
                st.toast("Application removed")
                st.rerun()

        st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 8px 0;' />", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
