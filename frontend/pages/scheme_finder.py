"""Multi-step guided eligibility form wizard."""

from typing import Callable
import streamlit as st
from frontend.services.api_client import api_client
from frontend.utils.i18n import t

INDIAN_STATES = [
    "ALL",
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
]

OCCUPATIONS = [
    "Farmer",
    "Agricultural Worker",
    "Student",
    "Self-Employed / Small Business",
    "Artisan / Craftsman",
    "Street Vendor / Hawker",
    "Salaried Employee",
    "Unemployed",
    "Senior Citizen / Retired",
    "Homemaker",
    "Other",
]


def render_scheme_finder(navigate_to: Callable[[str], None]) -> None:
    st.markdown("## 🧭 " + t("btn_find_schemes", "Find Schemes for Me"))
    st.caption("Answer a few simple questions to find government welfare benefits matching your circumstances.")

    # Initialize wizard step
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 1

    # Form profile state initialization
    if "finder_profile" not in st.session_state:
        st.session_state.finder_profile = {
            "state": "Uttar Pradesh",
            "district": "",
            "age": 32,
            "gender": "Female",
            "annual_income": 180000.0,
            "occupation": "Farmer",
            "category": "OBC",
            "area": "Rural",
            "disability": False,
            "requirement": "",
        }

    step = st.session_state.wizard_step
    prof = st.session_state.finder_profile

    # Progress Indicator
    progress = (step - 1) / 4.0
    st.progress(progress, text=f"Step {step} of 5 — {t(f'step{step}_title', '')}")

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container():
        # Step 1: Location
        if step == 1:
            st.subheader("📍 Step 1: Location & Domicile")
            st.write("Welfare schemes vary between Central Government and individual State Governments.")

            col1, col2 = st.columns(2)
            with col1:
                cur_state_idx = INDIAN_STATES.index(prof["state"]) if prof["state"] in INDIAN_STATES else 0
                prof["state"] = st.selectbox(t("label_state", "Select State / UT"), INDIAN_STATES, index=cur_state_idx)
            with col2:
                prof["district"] = st.text_input(t("label_district", "District (Optional)"), value=prof.get("district", ""))

        # Step 2: Age & Gender
        elif step == 2:
            st.subheader("👤 Step 2: Age & Gender")
            st.write("Many schemes target specific age groups (youth, elderly, children) or women empowerment.")

            col1, col2 = st.columns(2)
            with col1:
                prof["age"] = st.number_input(t("label_age", "Your Age"), min_value=0, max_value=120, value=int(prof.get("age", 30)))
            with col2:
                genders = ["Female", "Male", "Transgender", "Prefer not to say"]
                cur_g_idx = genders.index(prof["gender"]) if prof["gender"] in genders else 0
                prof["gender"] = st.selectbox(t("label_gender", "Gender"), genders, index=cur_g_idx)

        # Step 3: Income & Occupation
        elif step == 3:
            st.subheader("💼 Step 3: Income & Livelihood")
            st.write("Government criteria frequently use annual family income thresholds to target subsidies.")

            col1, col2 = st.columns(2)
            with col1:
                prof["annual_income"] = st.number_input(
                    t("label_income", "Annual Family Income (₹)"),
                    min_value=0.0,
                    max_value=10000000.0,
                    step=10000.0,
                    value=float(prof.get("annual_income", 150000.0)),
                    help="Total combined household earnings from all sources in rupees per year.",
                )
            with col2:
                cur_occ_idx = OCCUPATIONS.index(prof["occupation"]) if prof["occupation"] in OCCUPATIONS else 0
                prof["occupation"] = st.selectbox(t("label_occupation", "Primary Occupation"), OCCUPATIONS, index=cur_occ_idx)

        # Step 4: Social Category & Area
        elif step == 4:
            st.subheader("🏷️ Step 4: Social Category & Setting")
            st.write("Special reservations and benefits exist for specific social categories and rural/urban areas.")

            col1, col2 = st.columns(2)
            with col1:
                categories = ["General", "OBC", "SC", "ST", "EWS"]
                cur_c_idx = categories.index(prof["category"]) if prof["category"] in categories else 0
                prof["category"] = st.selectbox(t("label_category", "Social Category"), categories, index=cur_c_idx)
            with col2:
                areas = ["Rural", "Urban", "Semi-Urban"]
                cur_a_idx = areas.index(prof["area"]) if prof["area"] in areas else 0
                prof["area"] = st.selectbox(t("label_area", "Area of Residence"), areas, index=cur_a_idx)

        # Step 5: Special Needs & Requirements
        elif step == 5:
            st.subheader("🎯 Step 5: Special Needs & Focus")
            st.write("Highlight any specific assistance you are seeking (e.g. education scholarship, farm loan, healthcare).")

            prof["disability"] = st.checkbox(
                t("label_disability", "Person with Disability (Divyangjan)?"),
                value=bool(prof.get("disability", False)),
            )

            prof["requirement"] = st.text_input(
                t("label_requirement", "Specific Need or Focus (e.g., 'farm financial aid', 'daughter education', 'business loan')"),
                value=prof.get("requirement", ""),
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation buttons
    col_nav1, col_nav2, col_spacer = st.columns([2, 3, 5])
    with col_nav1:
        if step > 1:
            if st.button("⬅️ " + t("btn_back", "Back"), use_container_width=True):
                st.session_state.wizard_step -= 1
                st.rerun()

    with col_nav2:
        if step < 5:
            if st.button(t("btn_next", "Next Step") + " ➡️", type="primary", use_container_width=True):
                st.session_state.wizard_step += 1
                st.rerun()
        else:
            if st.button("🎯 " + t("btn_submit", "Find My Eligible Schemes"), type="primary", use_container_width=True):
                with st.spinner("Evaluating deterministic criteria across verified schemes..."):
                    # Submit to backend
                    res = api_client.match_schemes(prof)
                    if res["ok"]:
                        st.session_state.match_results = res["data"]
                        st.session_state.matched_profile = prof
                        navigate_to("results")
                    else:
                        st.error(f"Error evaluating schemes: {res['error']}")
