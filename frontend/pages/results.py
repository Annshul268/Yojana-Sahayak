"""Clean, human-centric Results page matching the civic design system."""

from typing import Callable
import streamlit as st
from frontend.components.eligibility_card import render_eligibility_card
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language
from frontend.utils.ui import inject_scroll_to_top


def render_results(navigate_to: Callable[[str], None]) -> None:
    lang = get_current_language()

    # Reset scroll to top if flagged
    if st.session_state.get("_scroll_to_top_needed", False):
        st.session_state["_scroll_to_top_needed"] = False
        inject_scroll_to_top(anchor_id="results-top")

    match_data = st.session_state.get("match_results")
    if not match_data:
        st.info("No active search yet. Fill out the quick form to discover schemes matching your profile.")
        if st.button("🚀 " + ("पात्रता जांचें" if lang == "hi" else "Check Eligibility"), type="primary"):
            st.session_state["_scroll_to_top_needed"] = True
            navigate_to("finder")
        return

    results = match_data.get("results", [])
    user_id = st.session_state.get("user_id", "citizen_user_1")

    # Fetch saved schemes
    saved_res = api_client.list_saved(user_id=user_id)
    saved_ids = set()
    if saved_res["ok"]:
        saved_ids = {s.get("scheme_id") for s in saved_res["data"]}

    # Clean Heading
    total_matches = match_data.get("total_schemes_evaluated", len(results))
    eligible_count = match_data.get("eligible_count", sum(1 for r in results if r.get("status") == "eligible"))
    pot_count = match_data.get("potentially_eligible_count", sum(1 for r in results if r.get("status") == "potentially_eligible"))

    st.markdown(
        f"""
        <div id="results-top" style="position: relative;">
            <div id="results-top-anchor" style="position: absolute; top: -20px; left: 0; height: 1px; width: 1px; opacity: 0; pointer-events: none;"></div>
        </div>
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px;">
                <h2 style="color: #0F172A; font-weight: 800; font-size: 1.75rem; margin-bottom: 4px;">
                    {"आपके लिए सरकारी योजनाएं" if lang == "hi" else "Government Schemes Matching Your Profile"}
                </h2>
                <span style="font-size: 0.85rem; color: #0F766E; font-weight: 600; background: #F0FDFA; border: 1px solid #CCFBF1; padding: 4px 10px; border-radius: 9999px;">
                    {eligible_count} {"पात्र योजनाएं" if lang == "hi" else "eligible"} · {pot_count} {"सत्यापन आवश्यक" if lang == "hi" else "need verification"} · {total_matches} {"मूल्यांकित" if lang == "hi" else "evaluated"}
                </span>
            </div>
            <p style="color: #64748B; font-size: 0.95rem; margin: 0;">
                {"आधिकारिक नियमों के आधार पर आपके विवरण से मेल खाने वाली योजनाएं और उनके लाभ नीचे दिए गए हैं।" if lang == "hi" else "Based on official eligibility rules, here are the schemes you qualify for, why they match, and how to apply."}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Simplified Filter Pills
    filter_choice = st.radio(
        "Filter results:",
        options=[
            f"Likely Eligible ({eligible_count})" if lang != "hi" else f"पात्र योजनाएं ({eligible_count})",
            f"All Evaluated ({total_matches})" if lang != "hi" else f"सभी योजनाएं ({total_matches})",
            f"Needs Verification ({pot_count})" if lang != "hi" else f"सत्यापन आवश्यक ({pot_count})",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )

    filtered = results
    if "Likely" in filter_choice or "पात्र" in filter_choice:
        filtered = [r for r in results if r.get("status") == "eligible"]
    elif "Needs" in filter_choice or "सत्यापन" in filter_choice:
        filtered = [r for r in results if r.get("status") == "potentially_eligible"]

    def handle_details(slug: str):
        st.session_state.selected_scheme_slug = slug
        st.session_state["_scheme_scroll_to_top"] = True
        navigate_to("scheme_details")

    def handle_save(scheme_id: str):
        if scheme_id in saved_ids:
            api_client.remove_saved_scheme(scheme_id=scheme_id, user_id=user_id)
            st.toast("Removed from bookmarks")
        else:
            api_client.save_scheme(scheme_id=scheme_id, user_id=user_id)
            st.toast("Saved to bookmarks ⭐")
        st.rerun()

    # Render Cards
    if not filtered:
        st.info("No schemes found under this filter.")
    else:
        for match in filtered:
            is_saved = match.get("scheme_id") in saved_ids
            render_eligibility_card(
                match=match,
                on_view_details=handle_details,
                on_save=handle_save,
                is_saved=is_saved,
            )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    c_btn1, c_btn2 = st.columns([1.5, 2])
    with c_btn1:
        if st.button("🔄 " + ("विवरण संशोधित करें" if lang == "hi" else "Edit Your Answers"), use_container_width=True):
            st.session_state["_scroll_to_top_needed"] = True
            navigate_to("finder")
    with c_btn2:
        if st.button("📚 " + ("सभी योजनाएं ब्राउज़ करें" if lang == "hi" else "Browse All Schemes Directory"), use_container_width=True):
            st.session_state["_scroll_to_top_needed"] = True
            navigate_to("schemes")
