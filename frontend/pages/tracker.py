"""Simple, linear Application Tracker view."""

from typing import Callable
import streamlit as st
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language, t

TRACKING_STAGES = [
    "Saved",
    "Planning to Apply",
    "Application Started",
    "Applied",
    "Completed",
]


def render_application_tracker(navigate_to: Callable[[str], None]) -> None:
    lang = get_current_language()
    user_id = st.session_state.get("user_id", "citizen_user_1")

    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="color: #1E3A8A; font-weight: 700; margin-bottom: 4px;">
                {"मेरे आवेदन" if lang == "hi" else "My Applications"}
            </h2>
            <p style="color: #6B7280; font-size: 0.95rem;">
                {"आवेदन प्रक्रिया के हर चरण में अपनी प्रगति को ट्रैक करें।" if lang == "hi" else "Track your progress through each application stage."}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    res = api_client.list_tracking(user_id=user_id)
    if not res["ok"]:
        st.error("Unable to load application trackers right now.")
        return

    entries = res["data"]
    if not entries:
        st.markdown(
            f"""
            <div style="background: white; border: 1px dashed #D1D5DB; border-radius: 8px; padding: 2.5rem 1.5rem; text-align: center; margin: 2rem 0;">
                <div style="font-size: 2rem; margin-bottom: 8px;">📝</div>
                <h4 style="color: #374151; margin-bottom: 6px;">{"कोई सक्रिय आवेदन नहीं" if lang == "hi" else "No tracked applications yet"}</h4>
                <p style="color: #6B7280; font-size: 0.9rem; max-width: 420px; margin: 0 auto 16px auto;">
                    {"योजना विवरण पृष्ठ से किसी भी योजना को अपनी ट्रैकर सूची में जोड़ें।" if lang == "hi" else "Add any scheme to your application tracker from its details page."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📚 " + ("योजनाएं खोजें" if lang == "hi" else "Browse Schemes"), type="primary"):
            navigate_to("schemes")
        return

    for entry in entries:
        scheme = entry.get("scheme", {})
        scheme_name = scheme.get("name_hi") if (lang == "hi" and scheme.get("name_hi")) else scheme.get("name", "Unknown Scheme")
        tracking_id = entry.get("id")
        current_status = entry.get("status", "Saved")
        notes = entry.get("notes", "")

        with st.container():
            st.markdown(
                f"""
                <div class="clean-card" style="margin-bottom: 12px; padding: 1.25rem;">
                    <h3 style="color: #1E3A8A; font-size: 1.15rem; font-weight: 700; margin: 0 0 8px 0;">
                        {scheme_name}
                    </h3>
                    <div style="font-size: 0.85rem; color: #4B5563; margin-bottom: 8px;">
                        Current Stage: <span style="font-weight: 600; color: #1E3A8A;">{current_status}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Simple stage dropdown & note
            c_st, c_notes, c_save = st.columns([3, 4, 2])
            with c_st:
                cur_idx = TRACKING_STAGES.index(current_status) if current_status in TRACKING_STAGES else 0
                new_status = st.selectbox(
                    "Stage:",
                    TRACKING_STAGES,
                    index=cur_idx,
                    key=f"sim_track_{tracking_id}",
                    label_visibility="collapsed",
                )
            with c_notes:
                new_notes = st.text_input(
                    "Note / Ref Number",
                    value=notes or "",
                    placeholder="e.g. Application No. or notes",
                    key=f"sim_notes_{tracking_id}",
                    label_visibility="collapsed",
                )
            with c_save:
                if st.button("Update 💾", key=f"sim_save_{tracking_id}", use_container_width=True):
                    api_client.update_tracking(
                        tracking_id=tracking_id,
                        status=new_status,
                        notes=new_notes,
                    )
                    st.toast("Application stage updated! ✅")
                    st.rerun()

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
