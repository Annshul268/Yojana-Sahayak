"""Scheme deep-dive details view."""

from typing import Callable
import streamlit as st
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language, t


def render_scheme_details(navigate_to: Callable[[str], None]) -> None:
    slug = st.session_state.get("selected_scheme_slug")
    if not slug:
        st.warning("No scheme selected.")
        if st.button("⬅️ Back to Directory"):
            navigate_to("schemes")
        return

    # Back action
    col_back, col_space = st.columns([2, 8])
    with col_back:
        if st.button("⬅️ Back to Directory", use_container_width=True):
            navigate_to("schemes")

    # Fetch scheme details
    res = api_client.get_scheme(slug)
    if not res["ok"]:
        st.error(f"Error loading scheme details: {res['error']}")
        return

    scheme = res["data"]
    lang = get_current_language()

    name = scheme.get("name_hi") if (lang == "hi" and scheme.get("name_hi")) else scheme.get("name", "")
    desc = scheme.get("description_hi") if (lang == "hi" and scheme.get("description_hi")) else scheme.get("description", "")
    category = scheme.get("category", "")
    ministry = scheme.get("ministry", "")
    official_url = scheme.get("official_url", "#")
    last_verified = scheme.get("last_verified_at", "Recently Verified")[:10]
    user_id = st.session_state.get("user_id", "guest_user_1")

    # Header Card
    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #CBD5E0; border-radius: 8px; padding: 1.5rem; margin: 12px 0 20px 0;">
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 8px;">
                <span style="background: #EDF2F7; color: #2D3748; padding: 3px 10px; border-radius: 4px; font-size: 0.8rem; font-weight: 600;">{category}</span>
                <span style="background: #C6F6D5; color: #22543D; padding: 3px 10px; border-radius: 4px; font-size: 0.8rem; font-weight: 700;">🛡️ Verified Government Scheme</span>
                <span style="color: #718096; font-size: 0.8rem;">Last Verified: {last_verified}</span>
            </div>
            <h1 style="color: #1A365D; margin: 6px 0 10px 0; font-size: 1.8rem;">{name}</h1>
            <p style="color: #4A5568; font-size: 1rem; line-height: 1.6; margin-bottom: 12px;">{desc}</p>
            <p style="color: #718096; font-size: 0.88rem; margin: 0;"><strong>Responsible Authority:</strong> {ministry}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_btn1, col_btn2, col_space = st.columns([3, 3, 4])
    with col_btn1:
        st.link_button(f"🔗 {t('btn_official_portal', 'Open Official Portal')}", official_url, type="primary", use_container_width=True)
    with col_btn2:
        if st.button("📋 Add to Application Tracker", use_container_width=True):
            track_res = api_client.create_tracking(
                user_id=user_id,
                scheme_id=scheme["id"],
                status="Planning to Apply",
                notes=f"Added from scheme details on {name}",
            )
            if track_res["ok"]:
                st.toast("Added to Application Tracker! 🚀")
                navigate_to("tracker")
            else:
                st.error(f"Could not track: {track_res['error']}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Detailed Tabs
    tab_benefits, tab_eligibility, tab_documents, tab_steps, tab_ai = st.tabs([
        "🎁 Scheme Benefits",
        "🎯 Eligibility Criteria",
        "📄 Required Documents",
        "📝 Application Procedure",
        "🤖 Grounded AI Q&A",
    ])

    with tab_benefits:
        st.subheader("Key Benefits Provided")
        benefits = scheme.get("benefits", [])
        if benefits:
            for b in benefits:
                st.markdown(f"- ✅ **{b}**")
        else:
            st.info("Benefit details are specified on the official portal.")

    with tab_eligibility:
        st.subheader("Deterministic Eligibility Rules")
        rules = scheme.get("eligibility_rules", {})
        if rules:
            st.json(rules)
        else:
            st.info("General eligibility criteria apply as per ministry guidelines.")

    with tab_documents:
        st.subheader("Documents Checklist for Verification")
        docs = scheme.get("documents", [])
        if docs:
            for d in docs:
                st.markdown(f"- 📄 **{d}**")
        else:
            st.info("Standard identity proof (Aadhaar, Bank Passbook, Address Proof) typically required.")

    with tab_steps:
        st.subheader("Step-by-Step How to Apply")
        steps = scheme.get("application_steps", [])
        if steps:
            for idx, s in enumerate(steps, 1):
                st.markdown(f"**Step {idx}:** {s}")
        else:
            st.info(f"Please refer to the official portal: [{official_url}]({official_url})")

    with tab_ai:
        st.subheader(f"Ask AI about {name}")
        st.caption("Responses are strictly grounded in verified government documents.")
        q = st.text_input("Enter your question:", placeholder="e.g. What is the maximum income ceiling or document needed?", key="tab_ai_q")
        if st.button("Ask Assistant", key="tab_ai_submit", type="primary"):
            if q.strip():
                with st.spinner("Retrieving verified facts and generating answer..."):
                    ai_res = api_client.ask_ai(question=f"{q} regarding {name}", language=lang)
                    if ai_res["ok"]:
                        st.markdown("#### 💡 Grounded Answer:")
                        st.markdown(ai_res["data"]["answer"])
                    else:
                        st.error(f"Error: {ai_res['error']}")
