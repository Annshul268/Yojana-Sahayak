"""Application progress tracker view."""

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
    st.markdown("## 📈 " + t("nav_tracker", "Application Tracker"))
    st.caption("Monitor your welfare scheme applications through every stage of fulfillment.")

    user_id = st.session_state.get("user_id", "guest_user_1")
    lang = get_current_language()

    with st.spinner("Fetching application stages..."):
        res = api_client.list_tracking(user_id=user_id)

    if not res["ok"]:
        st.error(f"Error loading tracker: {res['error']}")
        return

    entries = res["data"]
    if not entries:
        st.info("You are not tracking any scheme applications yet.")
        if st.button("🚀 Find Schemes to Track", type="primary"):
            navigate_to("schemes")
        return

    # Stage Counts
    counts = {stage: sum(1 for e in entries if e.get("status") == stage) for stage in TRACKING_STAGES}
    cols = st.columns(len(TRACKING_STAGES))
    for idx, stage in enumerate(TRACKING_STAGES):
        with cols[idx]:
            st.metric(stage, counts[stage])

    st.markdown("<hr style='margin: 12px 0 20px 0; border: none; border-top: 1px solid #E2E8F0;' />", unsafe_allow_html=True)

    # Filter tab
    selected_tab = st.selectbox("Filter by Stage:", ["All Stages"] + TRACKING_STAGES)
    filtered = entries if selected_tab == "All Stages" else [e for e in entries if e.get("status") == selected_tab]

    for entry in filtered:
        scheme = entry.get("scheme", {})
        scheme_name = scheme.get("name_hi") if (lang == "hi" and scheme.get("name_hi")) else scheme.get("name", "Unknown Scheme")
        tracking_id = entry.get("id")
        current_status = entry.get("status", "Saved")
        notes = entry.get("notes", "")

        with st.expander(f"📌 {scheme_name} — Stage: **{current_status}**", expanded=True):
            col_st, col_notes, col_act = st.columns([3, 4, 2])
            with col_st:
                cur_idx = TRACKING_STAGES.index(current_status) if current_status in TRACKING_STAGES else 0
                new_status = st.selectbox(
                    "Update Status:",
                    TRACKING_STAGES,
                    index=cur_idx,
                    key=f"status_sel_{tracking_id}",
                )
            with col_notes:
                new_notes = st.text_input(
                    "Notes / Ack Ref No:",
                    value=notes or "",
                    key=f"notes_input_{tracking_id}",
                )
            with col_act:
                st.write("")
                st.write("")
                if st.button("💾 Save", key=f"save_btn_{tracking_id}", use_container_width=True):
                    up_res = api_client.update_tracking(
                        tracking_id=tracking_id,
                        status=new_status,
                        notes=new_notes,
                    )
                    if up_res["ok"]:
                        st.toast("Application status updated! ✅")
                        st.rerun()
                    else:
                        st.error(f"Error updating: {up_res['error']}")

            col_del, col_space = st.columns([2, 8])
            with col_del:
                if st.button("🗑️ Remove Tracker", key=f"del_track_{tracking_id}"):
                    api_client.delete_tracking(tracking_id=tracking_id)
                    st.toast("Tracker removed")
                    st.rerun()
