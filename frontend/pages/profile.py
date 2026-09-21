"""Clean Citizen Profile view."""

from typing import Callable
import streamlit as st
from frontend.pages.scheme_finder import INDIAN_STATES, OCCUPATION_OPTIONS
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language, t


def render_citizen_profile(navigate_to: Callable[[str], None]) -> None:
    lang = get_current_language()
    user_id = st.session_state.get("user_id", "citizen_user_1")

    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="color: #1E3A8A; font-weight: 700; margin-bottom: 4px;">
                {"मेरी प्रोफ़ाइल" if lang == "hi" else "My Profile"}
            </h2>
            <p style="color: #6B7280; font-size: 0.95rem;">
                {"अपने बुनियादी विवरण अद्यतित रखें ताकि आपको सही योजनाओं की सिफारिशें मिल सकें।" if lang == "hi" else "Keep your details up to date for accurate automatic scheme recommendations."}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    res = api_client.get_profile(user_id=user_id)
    prof = res["data"] if res["ok"] else {}

    with st.form("clean_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", value=prof.get("name", "Citizen"))
            age = st.number_input("Age", min_value=0, max_value=120, value=int(prof.get("age") or 25))
            genders = ["Female", "Male", "Transgender", "Prefer not to say"]
            g_idx = genders.index(prof.get("gender")) if prof.get("gender") in genders else 0
            gender = st.selectbox("Gender", genders, index=g_idx)
            income = st.number_input(
                "Annual Income (₹)",
                min_value=0.0,
                max_value=10000000.0,
                step=10000.0,
                value=float(prof.get("annual_income") or 200000.0),
            )

        with col2:
            st_idx = INDIAN_STATES.index(prof.get("state")) if prof.get("state") in INDIAN_STATES else 0
            state = st.selectbox("State / UT", INDIAN_STATES, index=st_idx)
            occ_keys = [k for k, en, hi in OCCUPATION_OPTIONS]
            occ_labels = [hi if lang == "hi" else en for k, en, hi in OCCUPATION_OPTIONS]
            cur_occ = prof.get("occupation", "student")
            cur_occ_idx = occ_keys.index(cur_occ) if cur_occ in occ_keys else 0
            chosen_occ_lbl = st.selectbox("Occupation", occ_labels, index=cur_occ_idx)
            occupation = occ_keys[occ_labels.index(chosen_occ_lbl)]

            categories = ["General", "OBC", "SC", "ST", "EWS", "Prefer not to say"]
            c_idx = categories.index(prof.get("category")) if prof.get("category") in categories else 0
            category = st.selectbox("Category", categories, index=c_idx)
            area = st.radio("Area", ["Rural", "Urban"], index=0 if prof.get("area") == "Rural" else 1, horizontal=True)

        disability = st.checkbox("Person with Disability (Divyangjan)?", value=bool(prof.get("disability", False)))

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        if st.form_submit_button("Save Profile 💾", type="primary", use_container_width=True):
            updated_data = {
                "user_id": user_id,
                "name": name,
                "state": state,
                "age": age,
                "gender": gender,
                "annual_income": income,
                "occupation": occupation,
                "category": category,
                "area": area,
                "disability": disability,
            }
            api_client.upsert_profile(updated_data)
            st.session_state.user_name = name
            st.toast("Profile saved successfully! ✅")
            st.rerun()

    # Subtle Admin Login / Switcher in footer of profile for administrators
    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border: none; border-top: 1px solid #E5E7EB; margin: 20px 0;' />", unsafe_allow_html=True)

    with st.expander("🔐 Staff / Administrator Access", expanded=False):
        st.caption("Restricted to verified department administrators.")
        admin_pass = st.text_input("Enter Admin Access Code:", type="password")
        if st.button("Access Admin Dashboard"):
            if admin_pass == "admin" or admin_pass == "yojana2026":
                st.session_state.is_admin = True
                navigate_to("admin")
            else:
                st.error("Invalid access code.")
