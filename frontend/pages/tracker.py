"""My Applications - Dedicated Citizen Application Tracking View."""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import streamlit as st
from frontend.components.featured_carousel import get_scheme_banner_image
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language, t

APPLICATION_STATUSES = [
    "Saved",
    "Planning to Apply",
    "Applied",
    "Application Submitted",
    "Completed",
]


def format_date_str(dt_val: Any) -> str:
    """Format datetime or ISO string to clean display string (e.g. 25 Sep 2026)."""
    if not dt_val:
        return ""
    if isinstance(dt_val, datetime):
        return dt_val.strftime("%d %b %Y")
    if isinstance(dt_val, str):
        try:
            cleaned = dt_val.replace("Z", "+00:00")
            dt = datetime.fromisoformat(cleaned)
            return dt.strftime("%d %b %Y")
        except Exception:
            return dt_val[:10]
    return str(dt_val)


def render_application_tracker(navigate_to: Callable[[str], None]) -> None:
    """Renders the dedicated 'My Applications' page."""
    lang = get_current_language()
    is_authenticated = bool(st.session_state.get("is_authenticated", False))
    user_id = st.session_state.get("user_id", "")
    user_name = st.session_state.get("user_name", "Citizen")

    # Page Header
    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            <div style="display: inline-flex; align-items: center; gap: 6px; background: #EFF6FF; color: #1D4ED8; font-size: 0.8rem; font-weight: 700; padding: 4px 12px; border-radius: 9999px; margin-bottom: 8px;">
                <span>📋</span>
                <span>{"नागरिक सेवा ट्रैकर" if lang == "hi" else "Citizen Service Tracker"}</span>
            </div>
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
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 2.5rem 2rem; text-align: center; max-width: 620px; margin: 2rem auto; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);">
                <div style="font-size: 2.5rem; margin-bottom: 12px;">🔐</div>
                <h3 style="color: #0F172A; font-weight: 700; margin-bottom: 8px;">
                    {"अपने आवेदन देखने के लिए साइन इन करें" if lang == "hi" else "Sign In to Access My Applications"}
                </h3>
                <p style="color: #64748B; font-size: 0.95rem; line-height: 1.6; margin-bottom: 24px;">
                    {"आपके द्वारा जोड़े गए आवेदन सुरक्षित और केवल आपके खाते से जुड़े हैं। अपने आवेदनों को देखने और उनकी स्थिति ट्रैक करने के लिए साइन इन करें।" if lang == "hi" else "Your saved applications are private and associated with your citizen account. Please sign in to view, manage, and track your applications."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
        with col_c2:
            st.markdown("##### " + ("त्वरित साइन इन" if lang == "hi" else "Quick Sign In"))
            c_name = st.text_input("Name", value="Aarav Sharma", key="app_login_name")
            c_uid = st.text_input("Citizen ID", value="citizen_user_1", key="app_login_uid")

            col_sub1, col_sub2 = st.columns(2, gap="small")
            with col_sub1:
                if st.button("Sign In →" if lang != "hi" else "साइन इन करें →", type="primary", use_container_width=True):
                    st.session_state.is_authenticated = True
                    st.session_state.user_id = c_uid or "citizen_user_1"
                    st.session_state.user_name = c_name or "Citizen"
                    st.toast("Signed in successfully! 🎉")
                    st.rerun()
            with col_sub2:
                if st.button("Sign in as Priya (Demo)", type="secondary", use_container_width=True):
                    st.session_state.is_authenticated = True
                    st.session_state.user_id = "citizen_user_2"
                    st.session_state.user_name = "Priya Patel"
                    st.toast("Signed in as Priya Patel! 🎉")
                    st.rerun()

        return

    # 2. Authenticated Citizen Banner
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px 16px; margin-bottom: 24px;">
            <div style="font-size: 0.92rem; color: #334155;">
                {"लॉगिन उपयोगकर्ता:" if lang == "hi" else "Active Citizen:"} <strong>{user_name}</strong> <span style="color: #64748B;">({user_id})</span>
            </div>
            <div style="font-size: 0.85rem; color: #059669; font-weight: 600;">
                ✓ {"सत्यापित सत्र" if lang == "hi" else "Authenticated Session"}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Retrieve Applications
    res = api_client.list_tracking(user_id=user_id)
    entries = res.get("data", []) if res.get("ok") else []

    # 4. Empty State
    if not entries:
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 2px dashed #E2E8F0; border-radius: 16px; padding: 3.5rem 2rem; text-align: center; margin: 1.5rem 0;">
                <div style="font-size: 3rem; margin-bottom: 12px;">📝</div>
                <h3 style="color: #0F172A; font-weight: 700; margin-bottom: 8px;">
                    {"अभी तक कोई आवेदन नहीं" if lang == "hi" else "No applications yet"}
                </h3>
                <p style="color: #64748B; font-size: 0.98rem; max-width: 480px; margin: 0 auto 24px auto; line-height: 1.6;">
                    {"उन सरकारी लाभों पर नज़र रखने के लिए यहाँ योजनाएं जोड़ें जिनके लिए आप आवेदन करने की योजना बना रहे हैं।" if lang == "hi" else "Save schemes here to keep track of the government benefits you're planning to apply for."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_emp1, col_emp2, col_emp3 = st.columns([1.5, 2, 1.5])
        with col_emp2:
            browse_label = "📚 " + ("योजनाएं ब्राउज़ करें" if lang == "hi" else "Browse Schemes")
            if st.button(browse_label, type="primary", use_container_width=True, key="empty_browse_btn"):
                navigate_to("schemes")
        return

    # 5. Display Application Cards Grid
    col_grid_left, col_grid_right = st.columns(2, gap="large")

    for idx, entry in enumerate(entries):
        tracking_id = entry.get("id")
        current_status = entry.get("status", "Saved")
        created_at_val = entry.get("added_at") or entry.get("created_at")
        applied_at_val = entry.get("applied_at")
        notes_val = entry.get("notes", "")

        scheme = entry.get("scheme") or {}
        scheme_name = scheme.get("name_hi") if (lang == "hi" and scheme.get("name_hi")) else scheme.get("name", "Unknown Scheme")
        slug = scheme.get("slug", "")
        category = scheme.get("category", "General")
        level = scheme.get("level", "Central")
        states = scheme.get("states", ["ALL"])
        state_label = states[0] if (level != "Central" and states and "ALL" not in states) else ("केंद्रीय योजना" if lang == "hi" else "Central Scheme")

        banner_url = get_scheme_banner_image(category, slug, scheme.get("image_url"))
        added_date_str = format_date_str(created_at_val)
        applied_date_str = format_date_str(applied_at_val)

        # Status Badge Color Mapping
        status_colors = {
            "Saved": {"bg": "#F1F5F9", "color": "#475569", "border": "#CBD5E1"},
            "Planning to Apply": {"bg": "#FEF3C7", "color": "#B45309", "border": "#FDE68A"},
            "Application Started": {"bg": "#EFF6FF", "color": "#1D4ED8", "border": "#BFDBFE"},
            "Applied": {"bg": "#DBEAFE", "color": "#1E40AF", "border": "#93C5FD"},
            "Application Submitted": {"bg": "#E0E7FF", "color": "#3730A3", "border": "#C7D2FE"},
            "Completed": {"bg": "#DCFCE7", "color": "#15803D", "border": "#86EFAC"},
        }
        st_cfg = status_colors.get(current_status, status_colors["Saved"])

        target_col = col_grid_left if idx % 2 == 0 else col_grid_right

        with target_col:
            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; overflow: hidden; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05); display: flex; flex-direction: column;">
                    <div style="width: 100%; height: 160px; overflow: hidden; background: #0F172A; position: relative;">
                        <img src="{banner_url}" alt="{scheme_name}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='https://images.unsplash.com/photo-1532375810709-75b1da00537c?auto=format&fit=crop&w=700&q=80';" />
                        <div style="position: absolute; top: 10px; right: 10px; background: {st_cfg['bg']}; color: {st_cfg['color']}; border: 1px solid {st_cfg['border']}; font-size: 0.76rem; font-weight: 700; padding: 4px 10px; border-radius: 9999px;">
                            {current_status}
                        </div>
                    </div>
                    <div style="padding: 16px 18px 12px 18px; display: flex; flex-direction: column; flex: 1;">
                        <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                            <span style="background: #EFF6FF; color: #1D4ED8; border: 1px solid #DBEAFE; font-size: 0.74rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">
                                {category}
                            </span>
                            <span style="background: #F8FAFC; color: #334155; border: 1px solid #E2E8F0; font-size: 0.74rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">
                                {state_label}
                            </span>
                        </div>
                        <h3 style="font-size: 1.15rem; font-weight: 800; color: #0F172A; margin: 0 0 8px 0; line-height: 1.35; min-height: 2.7em;">
                            {scheme_name}
                        </h3>
                        <div style="font-size: 0.84rem; color: #64748B; margin-bottom: 12px;">
                            <span>Added on: <strong>{added_date_str or 'Recent'}</strong></span>
                            {f'<span style="margin-left: 10px; color: #1D4ED8;">• Applied on: <strong>{applied_date_str}</strong></span>' if applied_date_str and current_status in ('Applied', 'Application Submitted', 'Completed') else ''}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Interactive Status Selector & Notes
            c_sel, c_act = st.columns([1.2, 1], gap="small")
            with c_sel:
                cur_status_idx = (
                    APPLICATION_STATUSES.index(current_status)
                    if current_status in APPLICATION_STATUSES
                    else 0
                )
                new_status = st.selectbox(
                    "Status",
                    APPLICATION_STATUSES,
                    index=cur_status_idx,
                    key=f"status_sel_{tracking_id}",
                    label_visibility="collapsed",
                )
                if new_status != current_status:
                    api_client.update_tracking(
                        tracking_id=tracking_id,
                        user_id=user_id,
                        status=new_status,
                    )
                    st.toast(f"Status updated to: {new_status} ✅")
                    st.rerun()

            with c_act:
                col_sub_v, col_sub_r = st.columns([1, 1], gap="small")
                with col_sub_v:
                    if st.button("View Scheme →", key=f"view_scheme_btn_{tracking_id}", type="primary", use_container_width=True):
                        st.session_state.selected_scheme_slug = slug
                        navigate_to("scheme_details")
                with col_sub_r:
                    if st.button("Remove 🗑️", key=f"remove_app_btn_{tracking_id}", type="secondary", use_container_width=True):
                        api_client.delete_tracking(tracking_id=tracking_id, user_id=user_id)
                        st.toast("Application removed from list 🗑️")
                        st.rerun()

            st.markdown("<hr style='border: none; border-top: 1px solid #F1F5F9; margin: 10px 0 20px 0;' />", unsafe_allow_html=True)
