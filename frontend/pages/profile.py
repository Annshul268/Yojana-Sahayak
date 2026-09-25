"""Citizen Profile & Authentication Management View."""

from typing import Callable
import streamlit as st
from frontend.pages.scheme_finder import INDIAN_STATES, OCCUPATION_OPTIONS
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language, t


def render_citizen_profile(navigate_to: Callable[[str], None]) -> None:
    lang = get_current_language()
    is_authenticated = bool(st.session_state.get("is_authenticated", False))
    user_id = st.session_state.get("user_id", "")
    user_name = st.session_state.get("user_name", "Citizen")

    # Header
    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="color: #1E3A8A; font-size: 2.1rem; font-weight: 800; margin-bottom: 4px;">
                {"नागरिक प्रोफ़ाइल एवं खाता" if lang == "hi" else "Citizen Profile & Account"}
            </h1>
            <p style="color: #64748B; font-size: 0.95rem;">
                {"अपने आवेदन और प्रोफ़ाइल विवरण को सुरक्षित रूप से प्रबंधित करें।" if lang == "hi" else "Manage your personal profile, applications, and authentication settings securely."}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Authentication Status / Sign In Box
    if not is_authenticated:
        st.markdown(
            f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.75rem; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                    <span style="font-size: 1.5rem;">👤</span>
                    <h3 style="color: #0F172A; margin: 0; font-weight: 700;">
                        {"साइन इन करें" if lang == "hi" else "Sign In to Your Citizen Account"}
                    </h3>
                </div>
                <p style="color: #64748B; font-size: 0.9rem; margin-bottom: 16px;">
                    {"अपने आवेदनों को ट्रैक करने और व्यक्तिगत सिफारिशें प्राप्त करने के लिए साइन इन करें।" if lang == "hi" else "Sign in to track your government applications, access bookmarks, and receive personalized scheme eligibility."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_l1, col_l2 = st.columns(2, gap="large")
        with col_l1:
            st.markdown("##### " + ("विवरण दर्ज करें" if lang == "hi" else "Enter Account Details"))
            sign_name = st.text_input("Full Name", value="Aarav Sharma", key="prof_sign_name")
            sign_uid = st.text_input("Citizen ID / Mobile Number", value="citizen_user_1", key="prof_sign_uid")

            if st.button("Sign In →" if lang != "hi" else "साइन इन करें →", type="primary", use_container_width=True, key="btn_prof_signin"):
                st.session_state.is_authenticated = True
                st.session_state.user_id = sign_uid or "citizen_user_1"
                st.session_state.user_name = sign_name or "Citizen"
                target = st.session_state.pop("auth_redirect_target", None)
                st.toast(f"Welcome, {sign_name}! 🎉")
                if target:
                    navigate_to(target)
                else:
                    st.rerun()

        with col_l2:
            st.markdown("##### " + ("डेमो खाते" if lang == "hi" else "Quick Demo Accounts"))
            st.caption("Switch between demo citizen profiles to test application isolation:")

            if st.button("👤 Sign in as Citizen 1: Aarav Sharma (Delhi)", use_container_width=True, key="btn_demo_u1"):
                st.session_state.is_authenticated = True
                st.session_state.user_id = "citizen_user_1"
                st.session_state.user_name = "Aarav Sharma"
                target = st.session_state.pop("auth_redirect_target", None)
                st.toast("Signed in as Aarav Sharma! 🎉")
                if target:
                    navigate_to(target)
                else:
                    st.rerun()

            if st.button("👤 Sign in as Citizen 2: Priya Patel (Maharashtra)", use_container_width=True, key="btn_demo_u2"):
                st.session_state.is_authenticated = True
                st.session_state.user_id = "citizen_user_2"
                st.session_state.user_name = "Priya Patel"
                target = st.session_state.pop("auth_redirect_target", None)
                st.toast("Signed in as Priya Patel! 🎉")
                if target:
                    navigate_to(target)
                else:
                    st.rerun()
        st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 24px 0;' />", unsafe_allow_html=True)
        return

    # User IS Authenticated
    col_acc1, col_acc2, col_acc3 = st.columns([4, 2, 2], gap="small")
    with col_acc1:
        st.markdown(
            f"""
            <div style="background: #EFF6FF; border: 1px solid #DBEAFE; border-radius: 10px; padding: 12px 18px;">
                <div style="font-size: 0.82rem; color: #1D4ED8; font-weight: 700; text-transform: uppercase;">
                    ✓ {"सक्रिय नागरिक खाता" if lang == "hi" else "Active Citizen Session"}
                </div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A;">
                    {user_name}
                </div>
                <div style="font-size: 0.85rem; color: #64748B;">
                    Citizen ID: <code>{user_id}</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_acc2:
        if st.button("📋 " + ("मेरे आवेदन" if lang == "hi" else "My Applications"), use_container_width=True, key="prof_to_apps"):
            navigate_to("tracker")
        if st.button("⭐ " + ("सहेजी गई योजनाएं" if lang == "hi" else "Saved Schemes"), use_container_width=True, key="prof_to_saved"):
            navigate_to("saved")
    with col_acc3:
        if st.button("🚪 " + ("साइन आउट" if lang == "hi" else "Sign Out"), type="secondary", use_container_width=True, key="prof_signout_btn"):
            st.session_state.is_authenticated = False
            st.session_state.user_id = ""
            st.session_state.user_name = "Citizen"
            st.toast("Signed out successfully. 👋")
            st.rerun()

    st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 24px 0;' />", unsafe_allow_html=True)

    # 2. Profile Details Form
    res = api_client.get_profile(user_id=user_id)
    prof = res["data"] if res.get("ok") else {}

    st.markdown("### " + ("व्यक्तिगत विवरण" if lang == "hi" else "Personal Eligibility Profile"))

    with st.form("clean_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", value=prof.get("name") or user_name)
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
            if admin_pass in ("admin", "yojana2026"):
                st.session_state.is_admin = True
                navigate_to("admin")
            else:
                st.error("Invalid access code.")
