"""Clean, modern Scheme Directory page with category and state filters."""

from typing import Callable, List
import streamlit as st
from frontend.components.scheme_card import render_scheme_card
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language

CATEGORY_MAP = [
    ("ALL", "All Schemes", "सभी योजनाएं"),
    ("Education & Learning", "Education & Scholarships", "शिक्षा एवं छात्रवृत्ति"),
    ("Social Security & Pension", "Pension & Social Security", "पेंशन एवं सामाजिक सुरक्षा"),
    ("Women & Child Development", "Women & Child Welfare", "महिला एवं बाल विकास"),
    ("Agriculture & Rural Development", "Agriculture & Farming", "कृषि एवं किसान कल्याण"),
    ("Business & Self Employment", "Business & Loans", "व्यवसाय एवं ऋण"),
    ("Healthcare", "Health & Wellness", "स्वास्थ्य एवं चिकित्सा"),
    ("Employment & Skills", "Employment & Skills", "रोजगार एवं कौशल"),
    ("Housing & Shelter", "Housing & Shelter", "आवास एवं आश्रय"),
    ("Differently Abled Support", "Disability Support", "दिव्यांगजन सहायता"),
    ("Financial Assistance", "Financial Assistance", "वित्तीय सहायता"),
    ("Social Welfare", "Social Welfare", "समाज कल्याण"),
]

MAJOR_STATES = [
    "All States",
    "Andhra Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Delhi",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Tamil Nadu",
    "Telangana",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
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
                {"सत्यापित सरकारी कल्याणकारी योजनाओं की संपूर्ण सूची देखें, खोजें या श्रेणी और राज्य अनुसार छानें।" if lang == "hi" else "Explore verified Central and State welfare programs across key categories and states."}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Search and State Filter Row
    col_search, col_state = st.columns([7, 3])

    with col_search:
        search_query = st.text_input(
            "Search schemes",
            placeholder="🔍 " + ("योजना का नाम, मंत्रालय या लाभ खोजें..." if lang == "hi" else "Search schemes by name, ministry, or benefits..."),
            label_visibility="collapsed",
            key="schemes_search_input",
        )

    # State filter selection
    preselected_state = st.session_state.pop("selected_state_filter", None)
    default_state_idx = 0
    if preselected_state and preselected_state in MAJOR_STATES:
        default_state_idx = MAJOR_STATES.index(preselected_state)

    with col_state:
        selected_state = st.selectbox(
            "Filter by State / UT",
            options=MAJOR_STATES,
            index=default_state_idx,
            label_visibility="collapsed",
            key="schemes_state_select",
        )

    # 2. Category Filter Radio
    cat_keys = [k for k, en, hi in CATEGORY_MAP]
    cat_labels = [hi if lang == "hi" else en for k, en, hi in CATEGORY_MAP]

    preselected_cat = st.session_state.pop("selected_category_filter", None)
    default_cat_idx = 0
    if preselected_cat:
        for idx, (k, en, hi) in enumerate(CATEGORY_MAP):
            if preselected_cat.lower() in (k.lower(), en.lower(), hi.lower()):
                default_cat_idx = idx
                break

    chosen_cat_label = st.radio(
        "Categories:",
        options=cat_labels,
        index=default_cat_idx,
        horizontal=True,
        label_visibility="collapsed",
        key="schemes_category_radio",
    )
    selected_category = cat_keys[cat_labels.index(chosen_cat_label)]

    st.markdown("<hr style='border: none; border-top: 1px solid #E5E7EB; margin: 14px 0 20px 0;' />", unsafe_allow_html=True)

    # Fetch schemes from backend
    user_id = st.session_state.get("user_id", "citizen_user_1")
    state_param = selected_state if selected_state != "All States" else None

    res = api_client.list_schemes(
        q=search_query.strip() if search_query else None,
        category=selected_category if selected_category != "ALL" else None,
        state=state_param,
        page=1,
        page_size=100,
    )

    saved_res = api_client.list_saved(user_id=user_id)
    saved_ids = {s.get("scheme_id") for s in saved_res["data"]} if saved_res["ok"] else set()

    if not res["ok"]:
        st.error("We couldn't connect to the schemes directory right now. Please verify backend service.")
        return

    items = res["data"].get("items", [])
    total_found = res["data"].get("total", len(items))

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
        state_context = f" in {selected_state}" if selected_state != "All States" else ""
        cat_context = f" under {chosen_cat_label}" if selected_category != "ALL" else ""
        st.caption(f"Showing {len(items)} of {total_found} verified government scheme{'s' if total_found != 1 else ''}{cat_context}{state_context}:")
        for scheme in items:
            render_scheme_card(
                scheme=scheme,
                on_details=on_details,
                on_save=on_save,
                is_saved=(scheme.get("id") in saved_ids),
            )
