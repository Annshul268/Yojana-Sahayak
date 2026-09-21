"""Scheme Directory page with search and multi-faceted filtering."""

from typing import Callable
import streamlit as st
from frontend.components.scheme_card import render_scheme_card
from frontend.services.api_client import api_client
from frontend.utils.i18n import t

CATEGORIES = [
    "ALL",
    "Agriculture & Rural Development",
    "Healthcare",
    "Housing & Shelter",
    "Business & Self Employment",
    "Women & Child Development",
    "Social Security & Pension",
    "Education & Learning",
    "Differently Abled Support",
]


def render_schemes_directory(navigate_to: Callable[[str], None]) -> None:
    st.markdown("## 📚 " + t("btn_browse_schemes", "Scheme Directory"))
    st.caption("Browse, search, and filter verified Central and State Government welfare initiatives.")

    # Search and Filter Controls
    col_search, col_cat, col_level = st.columns([4, 3, 2])
    with col_search:
        search_query = st.text_input(
            "🔍 Search Schemes",
            placeholder=t("search_placeholder", "Search schemes by name, keyword, or benefit..."),
            label_visibility="collapsed",
        )
    with col_cat:
        selected_category = st.selectbox(
            "Category",
            options=CATEGORIES,
            label_visibility="collapsed",
        )
    with col_level:
        selected_level = st.selectbox(
            "Level",
            options=["ALL", "Central", "State"],
            label_visibility="collapsed",
        )

    # Fetch schemes from backend
    user_id = st.session_state.get("user_id", "guest_user_1")
    with st.spinner("Fetching verified schemes..."):
        res = api_client.list_schemes(
            q=search_query if search_query else None,
            category=selected_category,
            level=selected_level,
            page=1,
            page_size=50,
        )

    # Fetch user's saved schemes to reflect bookmark status
    saved_res = api_client.list_saved(user_id=user_id)
    saved_ids = set()
    if saved_res["ok"]:
        saved_ids = {s.get("scheme_id") for s in saved_res["data"]}

    if not res["ok"]:
        st.error(f"Error loading scheme directory: {res['error']}")
        return

    data = res["data"]
    items = data.get("items", [])
    st.markdown(f"**Showing {len(items)} of {data.get('total', 0)} Schemes**")
    st.markdown("<hr style='margin: 8px 0 16px 0; border: none; border-top: 1px solid #E2E8F0;' />", unsafe_allow_html=True)

    def on_details(slug: str):
        st.session_state.selected_scheme_slug = slug
        navigate_to("scheme_details")

    def on_save(scheme_id: str):
        if scheme_id in saved_ids:
            rem_res = api_client.remove_saved_scheme(scheme_id=scheme_id, user_id=user_id)
            if rem_res["ok"]:
                st.toast("Scheme removed from bookmarks")
                st.rerun()
        else:
            save_res = api_client.save_scheme(scheme_id=scheme_id, user_id=user_id)
            if save_res["ok"]:
                st.toast("Scheme saved to bookmarks! ⭐")
                st.rerun()

    if not items:
        st.info("No government schemes match your criteria. Try adjusting your search or filters.")
    else:
        for scheme in items:
            is_saved = scheme.get("id") in saved_ids
            render_scheme_card(
                scheme=scheme,
                on_details=on_details,
                on_save=on_save,
                is_saved=is_saved,
            )
