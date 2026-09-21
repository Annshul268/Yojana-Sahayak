"""Citizen profile view."""

from typing import Callable
import streamlit as st
from frontend.pages.scheme_finder import INDIAN_STATES, OCCUPATIONS
from frontend.services.api_client import api_client
from frontend.utils.i18n import t


def render_citizen_profile(navigate_to: Callable[[str], None]) -> None:
    st.markdown("## 👤 " + t("nav_profile", "My Profile"))
    st.caption("Keep your demographic details up to date to receive accurate automated scheme recommendations.")

    user_id = st.session_state.get("user_id", "guest_user_1")

    # Fetch existing profile
    with st.spinner("Loading profile..."):
        res = api_client.get_profile(user_id=user_id)

    prof = res["data"] if res["ok"] else {}

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", value=prof.get("name", "Citizen"))
            age = st.number_input("Age (Years)", min_value=0, max_value=120, value=int(prof.get("age") or 30))
            gender_options = ["Female", "Male", "Transgender", "Other"]
            g_idx = gender_options.index(prof.get("gender")) if prof.get("gender") in gender_options else 0
            gender = st.selectbox("Gender", gender_options, index=g_idx)
            income = st.number_input(
                "Annual Family Income (₹)",
                min_value=0.0,
                max_value=10000000.0,
                step=10000.0,
                value=float(prof.get("annual_income") or 150000.0),
            )

        with col2:
            st_idx = INDIAN_STATES.index(prof.get("state")) if prof.get("state") in INDIAN_STATES else 0
            state = st.selectbox("State / UT", INDIAN_STATES, index=st_idx)
            district = st.text_input("District", value=prof.get("district", ""))
            occ_idx = OCCUPATIONS.index(prof.get("occupation")) if prof.get("occupation") in OCCUPATIONS else 0
            occupation = st.selectbox("Primary Occupation", OCCUPATIONS, index=occ_idx)
            categories = ["General", "OBC", "SC", "ST", "EWS"]
            c_idx = categories.index(prof.get("category")) if prof.get("category") in categories else 0
            category = st.selectbox("Social Category", categories, index=c_idx)

        col3, col4 = st.columns(2)
        with col3:
            areas = ["Rural", "Urban", "Semi-Urban"]
            a_idx = areas.index(prof.get("area")) if prof.get("area") in areas else 0
            area = st.selectbox("Area of Residence", areas, index=a_idx)
        with col4:
            disability = st.checkbox("Person with Disability (Divyangjan)?", value=bool(prof.get("disability", False)))

        submit = st.form_submit_button("💾 Save Profile", type="primary", use_container_width=True)

    if submit:
        update_data = {
            "user_id": user_id,
            "name": name,
            "state": state,
            "district": district,
            "age": age,
            "gender": gender,
            "annual_income": income,
            "occupation": occupation,
            "category": category,
            "area": area,
            "disability": disability,
        }
        save_res = api_client.upsert_profile(update_data)
        if save_res["ok"]:
            st.session_state.user_name = name
            st.session_state.finder_profile = update_data
            st.toast("Profile updated successfully! ✅")
            st.rerun()
        else:
            st.error(f"Failed to update profile: {save_res['error']}")
