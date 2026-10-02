"""Citizen Profile & Authentication Management View."""

from typing import Any, Callable, Dict, Optional
import streamlit as st
from frontend.pages.scheme_finder import (
    INDIAN_STATES,
    OCCUPATION_OPTIONS,
    clear_auth_return_context,
    apply_profile_to_answers,
)
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language, t


def get_profile_return_context() -> Optional[Dict[str, Any]]:
    """Retrieves extensible profile return context from session state."""
    ctx = st.session_state.get("profile_return_context")
    if isinstance(ctx, dict):
        return ctx
    if st.session_state.get("auth_return_page") == "finder":
        return {
            "source": "eligibility_autofill",
            "target_page": "finder",
            "intent": st.session_state.get("auth_return_category"),
            "questionnaire_step": st.session_state.get("auth_return_step", 1),
            "mode": st.session_state.get("auth_return_mode", "autofill"),
            "answers": st.session_state.get("auth_return_answers", {}),
        }
    return None


def render_citizen_profile(navigate_to: Callable[[str], None]) -> None:
    lang = get_current_language()
    is_authenticated = bool(st.session_state.get("is_authenticated", False))
    user_id = st.session_state.get("user_id", "")
    user_name = st.session_state.get("user_name") or "Citizen"

    def handle_eligibility_return(uid: str, profile_just_saved: bool = False, saved_profile: Optional[Dict[str, Any]] = None) -> bool:
        ctx = get_profile_return_context()
        if ctx and ctx.get("source") == "eligibility_autofill":
            if profile_just_saved:
                prof_res = api_client.get_profile(user_id=uid) if uid else {}
                db_data = prof_res.get("data") if prof_res and prof_res.get("ok") else {}
                p = dict(db_data) if isinstance(db_data, dict) else {}
                if saved_profile:
                    p.update({k: v for k, v in saved_profile.items() if v is not None})
                ret_intent = ctx.get("intent") or st.session_state.get("auth_return_category")
                if "eligibility_answers" not in st.session_state:
                    st.session_state.eligibility_answers = {}
                if ret_intent:
                    st.session_state.eligibility_answers["intent"] = ret_intent
                prior_answers = ctx.get("answers") or st.session_state.get("auth_return_answers") or {}
                for k, v in prior_answers.items():
                    st.session_state.eligibility_answers[k] = v
                if p:
                    apply_profile_to_answers(p, st.session_state.eligibility_answers, overwrite=False)
                st.session_state.fill_mode = "autofill"
                st.session_state.questionnaire_step = max(1, ctx.get("questionnaire_step", 1))
                st.session_state["_scroll_to_top_needed"] = True
                clear_auth_return_context()
                navigate_to("finder")
                return True

            res = api_client.get_profile(user_id=uid)
            p = res.get("data") if res and res.get("ok") else None
            if p and any([p.get("state"), p.get("age"), p.get("gender"), p.get("occupation"), p.get("annual_income")]):
                ret_intent = ctx.get("intent") or st.session_state.get("auth_return_category")
                if "eligibility_answers" not in st.session_state:
                    st.session_state.eligibility_answers = {}
                if ret_intent:
                    st.session_state.eligibility_answers["intent"] = ret_intent
                prior_answers = ctx.get("answers") or st.session_state.get("auth_return_answers") or {}
                for k, v in prior_answers.items():
                    st.session_state.eligibility_answers[k] = v
                apply_profile_to_answers(p, st.session_state.eligibility_answers, overwrite=False)
                st.session_state.fill_mode = "autofill"
                st.session_state.questionnaire_step = max(1, ctx.get("questionnaire_step", 1))
                st.session_state["_scroll_to_top_needed"] = True
                clear_auth_return_context()
                navigate_to("finder")
                return True
            else:
                st.toast("Signed in! Please complete your profile below to use Auto Fill.")
                st.rerun()
                return True
        return False

    # Back Link button
    back_label = "← " + ("पीछे" if lang == "hi" else "Back")

    def on_profile_back():
        ctx = get_profile_return_context()
        if ctx and ctx.get("source") == "eligibility_autofill":
            if ctx.get("intent"):
                st.session_state.pending_category_intent = ctx.get("intent")
            clear_auth_return_context()
            navigate_to("finder")
            return
        clear_auth_return_context()
        last_page = st.session_state.get("_last_rendered_page")
        if last_page and last_page not in ("profile", "scheme_details", "admin"):
            navigate_to(last_page)
        else:
            navigate_to("home")

    if st.button(back_label, key="profile_back_btn", on_click=on_profile_back):
        on_profile_back()

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

    # Eligibility Return Guidance Banner
    ctx = get_profile_return_context()
    if ctx and ctx.get("source") == "eligibility_autofill":
        ret_cat = (ctx.get("intent") or st.session_state.get("auth_return_category", "")).capitalize()
        st.markdown(
            f"""
            <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 12px; padding: 1.1rem 1.35rem; margin-bottom: 1.5rem;">
                <div style="font-weight: 700; color: #1E3A8A; font-size: 1.05rem; display: flex; align-items: center; gap: 8px;">
                    <span>⚡</span>
                    <span>{"पात्रता जांच पर वापस जाएं" if lang == "hi" else "Return to Eligibility Check"}</span>
                </div>
                <div style="font-size: 0.88rem; color: #2563EB; margin-top: 4px; line-height: 1.45;">
                    {"साइन इन करें या अपनी प्रोफ़ाइल सहेजें ताकि आपके विवरण योजना पात्रता फॉर्म में अपने आप भर जाएं।" if lang == "hi" else f"Sign in or complete your profile below to automatically fill your details for {ret_cat or 'your selected category'}."}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("← " + ("बिना प्रोफ़ाइल पात्रता जांच जारी रखें" if lang == "hi" else "Continue Eligibility Manually without Profile"), key="btn_return_manual_from_prof"):
            if ctx.get("intent"):
                st.session_state.pending_category_intent = ctx.get("intent")
            clear_auth_return_context()
            navigate_to("finder")
            return

    # 1. Authentication Status / Sign In & Registration Box
    if not is_authenticated:
        auth_mode = st.session_state.get("auth_mode", "sign_in")

        _, col_center, _ = st.columns([1, 2.2, 1])
        with col_center:
            if auth_mode == "sign_in":
                st.markdown(
                    f"""
                    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.75rem 2rem; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                        <div style="font-size: 1.35rem; font-weight: 800; color: #0F172A; margin-bottom: 6px;">
                            {"योजना सहायक में आपका स्वागत है" if lang == "hi" else "Welcome to Yojana Sahayak"}
                        </div>
                        <div style="font-size: 0.9rem; color: #64748B; line-height: 1.5;">
                            {"अपनी सहेजी गई प्रोफ़ाइल, आवेदनों और व्यक्तिगत पात्रता तक पहुंचने के लिए साइन इन करें।" if lang == "hi" else "Sign in to access your saved profile, applications, and personalized eligibility."}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                sign_email = st.text_input(
                    "Email" if lang != "hi" else "ईमेल",
                    value="",
                    placeholder="name@example.com",
                    key="auth_signin_email",
                )
                sign_pass = st.text_input(
                    "Password" if lang != "hi" else "पासवर्ड",
                    value="",
                    type="password",
                    placeholder="••••••••",
                    key="auth_signin_pass",
                )

                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                if st.button("Sign In" if lang != "hi" else "साइन इन करें", type="primary", use_container_width=True, key="btn_auth_signin"):
                    res = api_client.sign_in(sign_email, sign_pass)
                    if not res.get("ok"):
                        st.error(res.get("message", "Incorrect email or password."))
                    else:
                        user = res.get("data") or {}
                        st.session_state.is_authenticated = True
                        st.session_state.user_id = user.get("user_id", "")
                        st.session_state.user_name = user.get("name") or "Citizen"
                        st.toast(f"Welcome back, {st.session_state.user_name}!")

                        if handle_eligibility_return(st.session_state.user_id):
                            return
                        target = st.session_state.pop("auth_redirect_target", None)
                        if target:
                            navigate_to(target)
                        else:
                            st.rerun()

                st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div style="text-align: center; font-size: 0.9rem; color: #64748B; margin-bottom: 8px;">
                        {"खाता नहीं है?" if lang == "hi" else "Don't have an account?"}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Create an account" if lang != "hi" else "नया खाता बनाएं", key="btn_switch_signup", use_container_width=True):
                    st.session_state.auth_mode = "sign_up"
                    st.rerun()

            else:  # Sign Up Mode
                st.markdown(
                    f"""
                    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.75rem 2rem; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                        <div style="font-size: 1.35rem; font-weight: 800; color: #0F172A; margin-bottom: 6px;">
                            {"योजना सहायक खाता बनाएं" if lang == "hi" else "Create your Yojana Sahayak account"}
                        </div>
                        <div style="font-size: 0.9rem; color: #64748B; line-height: 1.5;">
                            {"योजनाएं खोजने, अपनी प्रोफ़ाइल सहेजने और आवेदनों को ट्रैक करने के लिए पंजीकरण करें।" if lang == "hi" else "Sign up to discover schemes, save your citizen profile, and track applications."}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                reg_name = st.text_input(
                    "Full Name" if lang != "hi" else "पूरा नाम",
                    value="",
                    placeholder="e.g. Rahul Kumar",
                    key="auth_signup_name",
                )
                reg_email = st.text_input(
                    "Email" if lang != "hi" else "ईमेल",
                    value="",
                    placeholder="name@example.com",
                    key="auth_signup_email",
                )
                reg_pass = st.text_input(
                    "Password" if lang != "hi" else "पासवर्ड",
                    value="",
                    type="password",
                    placeholder="At least 6 characters",
                    key="auth_signup_pass",
                )
                reg_confirm = st.text_input(
                    "Confirm Password" if lang != "hi" else "पासवर्ड की पुष्टि करें",
                    value="",
                    type="password",
                    placeholder="Re-enter password",
                    key="auth_signup_confirm",
                )

                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                if st.button("Create Account" if lang != "hi" else "खाता बनाएं", type="primary", use_container_width=True, key="btn_auth_signup"):
                    res = api_client.register_user(reg_name, reg_email, reg_pass, reg_confirm)
                    if not res.get("ok"):
                        st.error(res.get("message", "Unable to create account."))
                    else:
                        user = res.get("data") or {}
                        st.session_state.is_authenticated = True
                        st.session_state.user_id = user.get("user_id", "")
                        st.session_state.user_name = user.get("name") or reg_name.strip()
                        st.session_state.auth_mode = "sign_in"
                        st.toast(f"Account created successfully! Welcome, {st.session_state.user_name}.")

                        # If user arrived from Auto Fill flow, guide them to complete profile
                        if st.session_state.get("auth_return_page") == "finder":
                            st.toast("Please complete your profile below to use Auto Fill for your selected category.")
                            st.rerun()
                        else:
                            target = st.session_state.pop("auth_redirect_target", None)
                            if target:
                                navigate_to(target)
                            else:
                                st.rerun()

                st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div style="text-align: center; font-size: 0.9rem; color: #64748B; margin-bottom: 8px;">
                        {"पहले से खाता है?" if lang == "hi" else "Already have an account?"}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Sign In" if lang != "hi" else "साइन इन करें", key="btn_switch_signin", use_container_width=True):
                    st.session_state.auth_mode = "sign_in"
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
                    {"सक्रिय नागरिक खाता" if lang == "hi" else "Active Citizen Session"}
                </div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A;">
                    {user_name}
                </div>
                <div style="font-size: 0.85rem; color: #64748B;">
                    Account ID: <code>{user_id}</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_acc2:
        if st.button("मेरे आवेदन" if lang == "hi" else "My Applications", use_container_width=True, key="prof_to_apps"):
            navigate_to("tracker")
        if st.button("सहेजी गई योजनाएं" if lang == "hi" else "Saved Schemes", use_container_width=True, key="prof_to_saved"):
            navigate_to("saved")
    with col_acc3:
        if st.button("साइन आउट" if lang == "hi" else "Sign Out", type="secondary", use_container_width=True, key="prof_signout_btn"):
            st.session_state.is_authenticated = False
            st.session_state.user_id = ""
            st.session_state.user_name = None
            st.session_state.pop("auth_mode", None)
            st.session_state.pop("eligibility_answers", None)
            st.session_state.pop("adaptive_answers", None)
            st.session_state.pop("match_results", None)
            st.session_state.pop("matched_profile", None)
            st.session_state.pop("eligibility_profile", None)
            st.session_state.pop("finder_answers", None)
            st.session_state.pop("pending_category_intent", None)
            for k in list(st.session_state.keys()):
                if k.startswith("field_") or k.startswith("auth_"):
                    st.session_state.pop(k, None)
            st.toast("Signed out successfully.")
            st.rerun()

    st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 24px 0;' />", unsafe_allow_html=True)

    # 2. Profile Details Form
    res = api_client.get_profile(user_id=user_id)
    prof = res["data"] if res.get("ok") and isinstance(res.get("data"), dict) else {}

    st.markdown("### " + ("व्यक्तिगत विवरण" if lang == "hi" else "Personal Eligibility Profile"))

    with st.form("clean_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name_val = prof.get("name") or user_name or ""
            name = st.text_input("Name" if lang != "hi" else "नाम", value=name_val)

            raw_age = prof.get("age")
            age_val = int(raw_age) if raw_age is not None and str(raw_age).isdigit() else None
            age = st.number_input(
                "Age" if lang != "hi" else "आयु",
                min_value=0,
                max_value=120,
                value=age_val,
                placeholder="e.g. 25" if lang != "hi" else "उदा. 25",
            )

            genders = ["Female", "Male", "Transgender", "Prefer not to say"]
            cur_gender = prof.get("gender")
            g_idx = genders.index(cur_gender) if cur_gender in genders else None
            gender = st.selectbox(
                "Gender" if lang != "hi" else "लिंग",
                genders,
                index=g_idx,
                placeholder="Select Gender" if lang != "hi" else "लिंग चुनें",
            )

            raw_inc = prof.get("annual_income")
            inc_val = float(raw_inc) if raw_inc is not None and str(raw_inc).strip() != "" else None
            income = st.number_input(
                "Annual Income (₹)" if lang != "hi" else "वार्षिक आय (₹)",
                min_value=0.0,
                max_value=10000000.0,
                step=10000.0,
                value=inc_val,
                placeholder="e.g. 150000" if lang != "hi" else "उदा. 150000",
            )

        with col2:
            cur_state = prof.get("state")
            st_idx = INDIAN_STATES.index(cur_state) if cur_state in INDIAN_STATES else None
            state = st.selectbox(
                "State / UT" if lang != "hi" else "राज्य / केंद्र शासित प्रदेश",
                INDIAN_STATES,
                index=st_idx,
                placeholder="Select State / UT" if lang != "hi" else "राज्य / केंद्र शासित प्रदेश चुनें",
            )

            district_val = prof.get("district") or ""
            district = st.text_input(
                "District" if lang != "hi" else "जिला",
                value=district_val,
                placeholder="e.g. Lucknow" if lang != "hi" else "उदा. लखनऊ",
            )

            occ_keys = [k for k, en, hi in OCCUPATION_OPTIONS]
            occ_labels = [hi if lang == "hi" else en for k, en, hi in OCCUPATION_OPTIONS]
            cur_occ = prof.get("occupation")
            cur_occ_idx = occ_keys.index(cur_occ) if cur_occ in occ_keys else None
            chosen_occ_lbl = st.selectbox(
                "Occupation" if lang != "hi" else "व्यवसाय",
                occ_labels,
                index=cur_occ_idx,
                placeholder="Select Occupation" if lang != "hi" else "व्यवसाय चुनें",
            )
            occupation = occ_keys[occ_labels.index(chosen_occ_lbl)] if chosen_occ_lbl in occ_labels else None

            categories = ["General", "OBC", "SC", "ST", "EWS", "Prefer not to say"]
            cur_cat = prof.get("category")
            c_idx = categories.index(cur_cat) if cur_cat in categories else None
            category = st.selectbox(
                "Category" if lang != "hi" else "सामाजिक श्रेणी",
                categories,
                index=c_idx,
                placeholder="Select Category" if lang != "hi" else "श्रेणी चुनें",
            )

            cur_area = str(prof.get("area") or "").capitalize()
            area_idx = 0 if cur_area == "Rural" else (1 if cur_area == "Urban" else None)
            area = st.radio(
                "Area" if lang != "hi" else "क्षेत्र",
                ["Rural", "Urban"],
                index=area_idx,
                horizontal=True,
            )

        dis_val = bool(prof.get("disability", False))
        disability = st.checkbox(
            "Person with Disability (Divyangjan)?" if lang != "hi" else "दिव्यांगजन (Person with Disability)?",
            value=dis_val,
        )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        if st.form_submit_button("Save Profile" if lang != "hi" else "प्रोफ़ाइल सहेजें", type="primary", use_container_width=True):
            updated_data = {
                "user_id": user_id,
                "name": name.strip() if name else user_name,
                "state": state if state else None,
                "district": district.strip() if district else None,
                "age": int(age) if age is not None else None,
                "gender": gender if gender else None,
                "annual_income": float(income) if income is not None else None,
                "occupation": occupation if occupation else None,
                "category": category if category else None,
                "area": area if area else None,
                "disability": bool(disability),
            }
            api_client.upsert_profile(updated_data)
            st.session_state.user_name = updated_data["name"]
            ctx = get_profile_return_context()
            if ctx and ctx.get("source") == "eligibility_autofill":
                handle_eligibility_return(user_id, profile_just_saved=True, saved_profile=updated_data)
                return
            else:
                clear_auth_return_context()
                navigate_to("home")
                return

    # Subtle Admin Login / Switcher in footer of profile for administrators
    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border: none; border-top: 1px solid #E5E7EB; margin: 20px 0;' />", unsafe_allow_html=True)

    with st.expander("Staff / Administrator Access", expanded=False):
        st.caption("Restricted to verified department administrators.")
        admin_pass = st.text_input("Enter Admin Access Code:", type="password")
        if st.button("Access Admin Dashboard"):
            if admin_pass in ("admin", "yojana2026"):
                st.session_state.is_admin = True
                navigate_to("admin")
            else:
                st.error("Invalid access code.")
