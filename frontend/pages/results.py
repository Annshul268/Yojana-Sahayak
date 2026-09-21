"""Results page displaying evaluated scheme matches."""

from typing import Any, Callable, Dict
import streamlit as st
from frontend.components.eligibility_card import render_eligibility_card
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language, t


def render_results(navigate_to: Callable[[str], None]) -> None:
    st.markdown("## 📊 Your Scheme Eligibility Results")

    match_data = st.session_state.get("match_results")
    if not match_data:
        st.info("No active evaluation found. Please fill in your profile via the Scheme Finder.")
        if st.button("🚀 Go to Scheme Finder", type="primary"):
            navigate_to("finder")
        return

    results = match_data.get("results", [])
    eligible_count = match_data.get("eligible_count", 0)
    pot_count = match_data.get("potentially_eligible_count", 0)
    not_count = match_data.get("not_eligible_count", 0)

    # Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Evaluated", match_data.get("total_schemes_evaluated", 0))
    with col2:
        st.metric("✅ Fully Eligible", eligible_count)
    with col3:
        st.metric("⚠️ Potentially Eligible", pot_count)
    with col4:
        st.metric("❌ Not Eligible", not_count)

    st.markdown("<hr style='margin: 12px 0 20px 0; border: none; border-top: 1px solid #E2E8F0;' />", unsafe_allow_html=True)

    # Filter by Status
    status_filter = st.radio(
        "Filter results by status:",
        options=["All Schemes", "Eligible Only", "Potentially Eligible", "Not Eligible"],
        horizontal=True,
    )

    filtered_results = results
    if status_filter == "Eligible Only":
        filtered_results = [r for r in results if r.get("status") == "eligible"]
    elif status_filter == "Potentially Eligible":
        filtered_results = [r for r in results if r.get("status") == "potentially_eligible"]
    elif status_filter == "Not Eligible":
        filtered_results = [r for r in results if r.get("status") == "not_eligible"]

    # Active AI Explanation Dialog
    if "active_explanation" in st.session_state and st.session_state.active_explanation:
        expl_data = st.session_state.active_explanation
        st.info(f"### 🤖 AI Grounded Explanation: {expl_data['scheme_name']}")
        st.markdown(expl_data["text"])
        if st.button("✖️ Close Explanation"):
            st.session_state.active_explanation = None
            st.rerun()
        st.divider()

    def handle_explain(match_item: Dict[str, Any]):
        user_prof = st.session_state.get("matched_profile", {})
        lang = get_current_language()
        with st.spinner("Generating grounded explanation from verified records..."):
            res = api_client.explain_eligibility(
                match_result=match_item,
                user_profile=user_prof,
                language=lang,
            )
            if res["ok"]:
                st.session_state.active_explanation = {
                    "scheme_name": match_item.get("scheme_name"),
                    "text": res["data"]["explanation"],
                }
                st.rerun()
            else:
                st.error(f"Could not generate explanation: {res['error']}")

    def handle_details(slug: str):
        st.session_state.selected_scheme_slug = slug
        navigate_to("scheme_details")

    # Render Scheme Results Cards
    if not filtered_results:
        st.warning("No schemes match the selected filter.")
    else:
        for match in filtered_results:
            render_eligibility_card(
                match=match,
                on_explain=handle_explain,
                on_view_details=handle_details,
            )
