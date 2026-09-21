"""Clean, modern Scheme Directory page."""

from typing import Callable
import streamlit as st
from frontend.components.scheme_card import render_scheme_card
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language

CATEGORY_MAP = [
    ("ALL", "All Schemes", "सभी योजनाएं"),
    ("Education & Learning", "Education & scholarships", "शिक्षा एवं छात्रवृत्ति"),
    ("Healthcare", "Health", "स्वास्थ्य"),
    ("Housing & Shelter", "Housing", "आवास"),
    ("Agriculture & Rural Development", "Agriculture", "कृषि"),
    ("Business & Self Employment", "Business & loans", "व्यवसाय एवं ऋण"),
    ("Social Security & Pension", "Pension", "पेंशन"),
    ("Women & Child Development", "Women & child", "महिला एवं बाल विकास"),
    ("Differently Abled Support", "Disability support", "दिव्यांगजन सहायता"),
]


def render_schemes_directory(navigate_to: Callable[[str], None]) -> None:
    lang = get_current_language()

    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="color: #0F172A; font-weight: 800; font-size: 1.75rem; margin-bottom: 4px;">
                {"सरकारी योजनाएं देखें" if lang == "hi" else "Browse All Government Schemes"}
            </h2>
            <p style="color: #64748B; font-size: 0.95rem; margin: 0;">
                {"सत्यापित सरकारी कल्याणकारी योजनाओं की संपूर्ण सूची देखें, खोजें या श्रेणी अनुसार छानें।" if lang == "hi" else "Explore verified Central and State welfare programs across key categories."}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Search Bar
    search_query = st.text_input(
        "Search schemes",
        placeholder="🔍 " + ("योजना का नाम, मंत्रालय या लाभ खोजें..." if lang == "hi" else "Search schemes by name, ministry, or benefits..."),
        label_visibility="collapsed",
    )

    # 2. Category Filter Radio
    cat_keys = [k for k, en, hi in CATEGORY_MAP]
    cat_labels = [hi if lang == "hi" else en for k, en, hi in CATEGORY_MAP]

    chosen_cat_label = st.radio(
        "Categories:",
        options=cat_labels,
        horizontal=True,
        label_visibility="collapsed",
    )
    selected_category = cat_keys[cat_labels.index(chosen_cat_label)]

    st.markdown("<hr style='border: none; border-top: 1px solid #E5E7EB; margin: 14px 0 20px 0;' />", unsafe_allow_html=True)

    # Fetch schemes from backend
    user_id = st.session_state.get("user_id", "citizen_user_1")
    res = api_client.list_schemes(
        q=search_query.strip() if search_query else None,
        category=selected_category if selected_category != "ALL" else None,
        page=1,
        page_size=50,
    )

    saved_res = api_client.list_saved(user_id=user_id)
    saved_ids = {s.get("scheme_id") for s in saved_res["data"]} if saved_res["ok"] else set()

    if not res["ok"]:
        st.error("We couldn't connect to the schemes directory right now. Please verify backend service.")
        return

    items = res["data"].get("items", [])

    def on_details(slug: str):
        st.session_state.selected_scheme_slug = slug
        navigate_to("scheme_details")

    def on_save(scheme_id: str):
        if scheme_id in saved_ids:
            api_client.remove_saved_scheme(scheme_id=scheme_id, user_id=user_id)
            st.toast("Scheme removed from bookmarks")
        else:
            api_client.save_scheme(scheme_id=scheme_id, user_id=user_id)
            st.toast("Scheme saved ⭐")
        st.rerun()

    if not items:
        st.info("No schemes match your search or filter.")
    else:
        st.caption(f"Showing {len(items)} official government scheme{'s' if len(items) != 1 else ''}:")
        for scheme in items:
            render_scheme_card(
                scheme=scheme,
                on_details=on_details,
                on_save=on_save,
                is_saved=(scheme.get("id") in saved_ids),
            )
