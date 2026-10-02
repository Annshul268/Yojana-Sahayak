"""Sector-Aware Grouped Eligibility Questionnaire with Stable State & Validation."""

from typing import Any, Callable, Dict, Optional
import streamlit as st
from frontend.services.api_client import api_client
from frontend.services.questionnaire_engine import (
    INDIAN_STATES,
    OCCUPATION_OPTIONS,
    QuestionField,
    QuestionGroup,
    questionnaire_engine,
)
from frontend.utils.i18n import get_current_language
from frontend.utils.ui import inject_scroll_to_top


def reset_eligibility_session(keep_intent: Optional[str] = None) -> None:
    """Completely resets the questionnaire answers, results, and widget keys for a clean session."""
    if keep_intent:
        st.session_state.eligibility_answers = {"intent": keep_intent}
    else:
        st.session_state.eligibility_answers = {}
    st.session_state.adaptive_answers = st.session_state.eligibility_answers

    st.session_state.pop("match_results", None)
    st.session_state.pop("matched_profile", None)
    st.session_state.pop("eligibility_profile", None)
    st.session_state.pop("pending_category_intent", None)
    st.session_state.pop("finder_answers", None)
    st.session_state.validation_error = None

    # Clear all dynamic field widget keys so Streamlit does not preserve stale inputs
    for key in list(st.session_state.keys()):
        if key.startswith("field_"):
            st.session_state.pop(key, None)

    st.session_state.questionnaire_step = 1 if keep_intent else 0
    st.session_state["_scroll_to_top_needed"] = True


def apply_profile_to_answers(
    prof: Dict[str, Any],
    answers: Dict[str, Any],
    overwrite: bool = True,
) -> None:
    """Populates questionnaire answers from Citizen Profile data safely.

    Does NOT mutate or save back to the Citizen Profile in database.
    If overwrite is False, existing non-empty user answers are preserved.
    Synchronizes field_* widget keys in session state for instant UI update.
    """
    if not prof:
        return

    def _set_val(key: str, val: Any) -> None:
        if val is None or val == "":
            return
        if overwrite or key not in answers or answers[key] in (None, ""):
            answers[key] = val

    # 1. State
    state_val = prof.get("state")
    if state_val and state_val in INDIAN_STATES:
        _set_val("state", state_val)

    # 2. District
    district_val = prof.get("district")
    if district_val:
        _set_val("district", str(district_val).strip())

    # 3. Residence Area (Rural / Urban)
    area_val = prof.get("area")
    if area_val:
        area_str = str(area_val).strip().capitalize()
        if area_str in ("Rural", "Urban"):
            _set_val("area", area_str)

    # 4. Age
    age_val = prof.get("age")
    if age_val is not None and age_val != "":
        try:
            _set_val("age", float(age_val))
        except (ValueError, TypeError):
            pass

    # 5. Gender
    gender_val = str(prof.get("gender", "")).lower().strip()
    if "female" in gender_val:
        _set_val("gender", "female")
    elif "male" in gender_val:
        _set_val("gender", "male")
    elif "trans" in gender_val or "other" in gender_val:
        _set_val("gender", "other")
    elif "prefer" in gender_val:
        _set_val("gender", "prefer_not_to_say")

    # 6. Annual Income
    income_val = prof.get("annual_income") if prof.get("annual_income") is not None else prof.get("income")
    if income_val is not None and income_val != "":
        try:
            _set_val("annual_income", float(income_val))
        except (ValueError, TypeError):
            pass

    # 7. Social Category
    cat_val = prof.get("category") or prof.get("social_category")
    if cat_val:
        valid_cats = ["General", "OBC", "SC", "ST", "EWS"]
        for c in valid_cats:
            if c.lower() == str(cat_val).lower().strip():
                _set_val("social_category", c)
                break

    # 8. Disability
    dis_val = prof.get("disability")
    if isinstance(dis_val, bool):
        _set_val("disability", "yes" if dis_val else "no")
    elif isinstance(dis_val, str) and dis_val.strip():
        if dis_val.lower().strip() in ("yes", "true", "1"):
            _set_val("disability", "yes")
        elif dis_val.lower().strip() in ("no", "false", "0"):
            _set_val("disability", "no")

    # 9. Marital Status
    marital_val = str(prof.get("marital_status", "")).lower().strip()
    valid_marital = ["single", "married", "widowed", "divorced", "prefer_not_to_say"]
    if marital_val in valid_marital:
        _set_val("marital_status", marital_val)

    # 10. Minority Status
    min_val = prof.get("minority_status") if prof.get("minority_status") is not None else prof.get("minority")
    if isinstance(min_val, bool):
        _set_val("minority_status", "yes" if min_val else "no")
    elif isinstance(min_val, str) and min_val.strip():
        if min_val.lower().strip() in ("yes", "true", "1"):
            _set_val("minority_status", "yes")
        elif min_val.lower().strip() in ("no", "false", "0"):
            _set_val("minority_status", "no")

    # 11. Occupation
    occ_val = prof.get("occupation")
    if occ_val:
        _set_val("occupation", str(occ_val).strip())


def store_auth_return_context(
    category: str,
    step: int = 1,
    answers: Optional[Dict[str, Any]] = None,
    mode: str = "autofill",
) -> None:
    """Stores the specific questionnaire context before redirecting to authentication."""
    st.session_state["auth_return_page"] = "finder"
    st.session_state["auth_return_category"] = category
    st.session_state["auth_return_step"] = max(1, step)
    st.session_state["auth_return_mode"] = mode
    st.session_state["auth_return_autofill"] = True
    st.session_state["auth_return_answers"] = dict(answers or {})


def clear_auth_return_context() -> None:
    """Safely clears temporary auth return state after it has been consumed."""
    st.session_state.pop("auth_return_page", None)
    st.session_state.pop("auth_return_category", None)
    st.session_state.pop("auth_return_step", None)
    st.session_state.pop("auth_return_mode", None)
    st.session_state.pop("auth_return_autofill", None)
    st.session_state.pop("auth_return_answers", None)
    st.session_state.pop("autofill_prompt_active", None)
    st.session_state.pop("autofill_prompt_type", None)


def get_saved_profile_for_autofill() -> tuple[bool, Dict[str, Any]]:
    """Checks if the active user is authenticated and has a saved citizen profile.

    Returns:
        (has_saved_profile, profile_dict)
    """
    is_auth = bool(st.session_state.get("is_authenticated", False))
    user_id = st.session_state.get("user_id")
    if not is_auth or not user_id:
        return False, {}

    try:
        res = api_client.get_profile(user_id=user_id)
        if res and res.get("ok"):
            prof = res.get("data") or {}
            # Verify profile has meaningful user data
            has_data = any([
                prof.get("state"),
                prof.get("age"),
                prof.get("gender"),
                prof.get("name"),
                prof.get("annual_income"),
                prof.get("occupation"),
            ])
            if has_data:
                return True, prof
    except Exception:
        pass
    return False, {}


def handle_manual_fill(category_key: str) -> None:
    reset_eligibility_session(keep_intent=category_key)
    st.session_state.fill_mode = "manual"
    st.session_state.pop("pending_category_intent", None)
    st.session_state.pop("autofill_prompt_active", None)
    st.session_state.pop("autofill_prompt_type", None)
    st.session_state.questionnaire_step = 1
    st.session_state["_scroll_to_top_needed"] = True
    st.rerun()


def handle_auto_fill(
    category_key: str,
    prof: Optional[Dict[str, Any]] = None,
    overwrite: bool = True,
) -> None:
    if overwrite:
        reset_eligibility_session(keep_intent=category_key)
    else:
        if "eligibility_answers" not in st.session_state:
            st.session_state.eligibility_answers = {}
        st.session_state.eligibility_answers["intent"] = category_key
        st.session_state.adaptive_answers = st.session_state.eligibility_answers

    st.session_state.fill_mode = "autofill"

    if prof is None:
        user_id = st.session_state.get("user_id") or "citizen_user_1"
        try:
            res = api_client.get_profile(user_id=user_id)
            if res and res.get("ok"):
                prof = res.get("data", {}) or {}
        except Exception:
            prof = {}

    if prof:
        apply_profile_to_answers(prof, st.session_state.eligibility_answers, overwrite=overwrite)

    st.session_state.pop("pending_category_intent", None)
    st.session_state.pop("autofill_prompt_active", None)
    st.session_state.pop("autofill_prompt_type", None)
    if "questionnaire_step" not in st.session_state or st.session_state.questionnaire_step == 0:
        st.session_state.questionnaire_step = 1
    st.session_state["_scroll_to_top_needed"] = True
    st.rerun()


def _render_autofill_dialog_content(category_key: str, lang: str) -> None:
    # 1. Check if an auth / incomplete profile prompt is active for this category
    prompt_active = (st.session_state.get("autofill_prompt_active") == category_key)
    prompt_type = st.session_state.get("autofill_prompt_type", "not_signed_in")

    if prompt_active:
        if prompt_type == "not_signed_in":
            st.markdown(
                f"""
                <div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 12px; padding: 1.25rem; margin-bottom: 1.25rem;">
                    <div style="font-weight: 700; color: #0F172A; font-size: 1.15rem; margin-bottom: 6px;">
                        {"आपकी प्रोफ़ाइल अभी सहेजी नहीं गई है" if lang == "hi" else "Your profile isn't saved yet"}
                    </div>
                    <div style="font-size: 0.92rem; color: #475569; line-height: 1.5;">
                        {"अपनी सहेजी गई प्रोफ़ाइल जानकारी के साथ ऑटो फिल का उपयोग करने के लिए साइन इन करें।" if lang == "hi" else "Sign in to use Auto Fill with your saved profile information."}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("साइन इन करें" if lang == "hi" else "Sign In", type="primary", key="btn_prompt_signin", use_container_width=True):
                store_auth_return_context(
                    category=category_key,
                    step=st.session_state.get("questionnaire_step", 1),
                    answers=st.session_state.get("eligibility_answers", {}),
                    mode="autofill",
                )
                st.session_state.pop("pending_category_intent", None)
                st.session_state.pop("autofill_prompt_active", None)
                st.session_state.pop("autofill_prompt_type", None)
                nav_fn = st.session_state.get("_nav_fn")
                if nav_fn:
                    nav_fn("profile")
                else:
                    st.session_state.current_page = "profile"
                    st.rerun()

            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            if st.button("स्वयं भरें" if lang == "hi" else "Continue Manually", type="secondary", key="btn_prompt_continue_manual", use_container_width=True):
                st.session_state.pop("autofill_prompt_active", None)
                st.session_state.pop("autofill_prompt_type", None)
                handle_manual_fill(category_key)

            st.markdown("<div style='height: 0.25rem;'></div>", unsafe_allow_html=True)
            if st.button("← " + ("विकल्पों पर वापस जाएं" if lang == "hi" else "Back to options"), key="btn_prompt_back_opt", use_container_width=True):
                st.session_state.pop("autofill_prompt_active", None)
                st.session_state.pop("autofill_prompt_type", None)
                st.rerun()
            return

        elif prompt_type == "incomplete_profile":
            st.markdown(
                f"""
                <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 12px; padding: 1.25rem; margin-bottom: 1.25rem;">
                    <div style="font-weight: 700; color: #92400E; font-size: 1.15rem; margin-bottom: 6px;">
                        {"आपकी प्रोफ़ाइल अभी पूरी नहीं है" if lang == "hi" else "Your profile isn't complete yet"}
                    </div>
                    <div style="font-size: 0.92rem; color: #B45309; line-height: 1.5;">
                        {"ऑटो फिल का उपयोग करने के लिए अपनी प्रोफ़ाइल पूरी करें।" if lang == "hi" else "Complete your profile to use Auto Fill with your saved information."}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("प्रोफ़ाइल पूरी करें" if lang == "hi" else "Complete Profile", type="primary", key="btn_prompt_complete_prof", use_container_width=True):
                store_auth_return_context(
                    category=category_key,
                    step=st.session_state.get("questionnaire_step", 1),
                    answers=st.session_state.get("eligibility_answers", {}),
                    mode="autofill",
                )
                st.session_state.pop("pending_category_intent", None)
                st.session_state.pop("autofill_prompt_active", None)
                st.session_state.pop("autofill_prompt_type", None)
                nav_fn = st.session_state.get("_nav_fn")
                if nav_fn:
                    nav_fn("profile")
                else:
                    st.session_state.current_page = "profile"
                    st.rerun()

            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            if st.button("स्वयं भरें" if lang == "hi" else "Continue Manually", type="secondary", key="btn_prompt_inc_manual", use_container_width=True):
                st.session_state.pop("autofill_prompt_active", None)
                st.session_state.pop("autofill_prompt_type", None)
                handle_manual_fill(category_key)

            st.markdown("<div style='height: 0.25rem;'></div>", unsafe_allow_html=True)
            if st.button("← " + ("विकल्पों पर वापस जाएं" if lang == "hi" else "Back to options"), key="btn_prompt_back_opt2", use_container_width=True):
                st.session_state.pop("autofill_prompt_active", None)
                st.session_state.pop("autofill_prompt_type", None)
                st.rerun()
            return

    # 2. Standard Selection Dialog (Option 1: Fill Manually, Option 2: Auto Fill)
    st.markdown(
        f"""
        <div style="font-size: 0.95rem; color: #475569; margin-bottom: 1.25rem; line-height: 1.5;">
            {"कृपया चुनें कि आप अपनी पात्रता जांचने के लिए फॉर्म कैसे भरना चाहते हैं:" if lang == "hi" else "Choose how you would like to complete your details for scheme eligibility:"}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Option 1: Fill Manually
    st.markdown(
        f"""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1rem; margin-bottom: 0.6rem;">
            <div style="font-weight: 700; color: #0F172A; font-size: 1rem; margin-bottom: 4px;">
                {"स्वयं भरें" if lang == "hi" else "Fill Manually"}
            </div>
            <div style="font-size: 0.85rem; color: #64748B; line-height: 1.4;">
                {"अपने विवरण स्वयं दर्ज करें।" if lang == "hi" else "Enter your details yourself."}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("स्वयं भरें" if lang == "hi" else "Fill Manually", key="btn_fill_manual", use_container_width=True):
        handle_manual_fill(category_key)

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # Option 2: Auto Fill
    st.markdown(
        f"""
        <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 10px; padding: 1rem; margin-bottom: 0.6rem;">
            <div style="font-weight: 700; color: #1E3A8A; font-size: 1rem; margin-bottom: 4px;">
                {"ऑटो फिल" if lang == "hi" else "Auto Fill"}
            </div>
            <div style="font-size: 0.85rem; color: #3B82F6; line-height: 1.4;">
                {"अपनी नागरिक प्रोफ़ाइल में पहले से उपलब्ध जानकारी का उपयोग करें और उपलब्ध फ़ील्ड स्वचालित रूप से भरें।" if lang == "hi" else "Use the information already available in your Citizen Profile and fill the available fields automatically."}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("ऑटो फिल" if lang == "hi" else "Auto Fill", type="primary", key="btn_fill_autofill", use_container_width=True):
        has_profile, prof = get_saved_profile_for_autofill()
        if not st.session_state.get("is_authenticated", False):
            st.session_state["autofill_prompt_active"] = category_key
            st.session_state["autofill_prompt_type"] = "not_signed_in"
            st.rerun()
        elif not has_profile:
            st.session_state["autofill_prompt_active"] = category_key
            st.session_state["autofill_prompt_type"] = "incomplete_profile"
            st.rerun()
        else:
            handle_auto_fill(category_key, prof=prof, overwrite=True)


def _on_dialog_dismiss() -> None:
    st.session_state.pop("pending_category_intent", None)
    st.session_state.pop("autofill_prompt_active", None)
    st.session_state.pop("autofill_prompt_type", None)


@st.dialog("How would you like to fill your details?", width="small", on_dismiss=_on_dialog_dismiss)
def _autofill_dialog_en(category_key: str) -> None:
    _render_autofill_dialog_content(category_key, "en")


@st.dialog("आप अपने विवरण कैसे भरना चाहते हैं?", width="small", on_dismiss=_on_dialog_dismiss)
def _autofill_dialog_hi(category_key: str) -> None:
    _render_autofill_dialog_content(category_key, "hi")


def render_scheme_finder(navigate_to: Callable[[str], None]) -> None:
    lang = get_current_language()
    st.session_state["_nav_fn"] = navigate_to

    # 1. Initialize Single Canonical Answer Store
    if "eligibility_answers" not in st.session_state:
        st.session_state.eligibility_answers = {}

    # Alias for backward-compatibility
    st.session_state.adaptive_answers = st.session_state.eligibility_answers
    answers = st.session_state.eligibility_answers

    # 2. Check if returning from authentication with saved context
    if st.session_state.get("auth_return_page") == "finder" and st.session_state.get("is_authenticated", False):
        has_profile, prof = get_saved_profile_for_autofill()
        if has_profile:
            ret_category = st.session_state.get("auth_return_category")
            if ret_category:
                st.session_state.eligibility_answers["intent"] = ret_category
            ret_answers = st.session_state.get("auth_return_answers") or {}
            for k, v in ret_answers.items():
                st.session_state.eligibility_answers[k] = v
            apply_profile_to_answers(prof, st.session_state.eligibility_answers, overwrite=False)
            ret_step = st.session_state.get("auth_return_step", 1)
            st.session_state.questionnaire_step = max(1, ret_step)
            st.session_state.fill_mode = "autofill"
            st.session_state["_scroll_to_top_needed"] = True
            clear_auth_return_context()

    # Check if arrived from home category chip
    if "finder_answers" in st.session_state and "needs" in st.session_state.finder_answers:
        home_needs = st.session_state.finder_answers.get("needs", [])
        if home_needs and "intent" not in answers:
            first_need = home_needs[0].lower()
            mapped = "general"
            if "education" in first_need or "scholarship" in first_need:
                mapped = "education"
            elif "business" in first_need or "loan" in first_need:
                mapped = "business"
            elif "agri" in first_need:
                mapped = "agriculture"
            elif "intern" in first_need:
                mapped = "internships"
            elif "job" in first_need or "employ" in first_need:
                mapped = "jobs"
            elif "skill" in first_need:
                mapped = "skills"
            elif "housing" in first_need:
                mapped = "housing"
            elif "health" in first_need:
                mapped = "healthcare"
            elif "pension" in first_need:
                mapped = "pension"
            elif "women" in first_need or "child" in first_need:
                mapped = "women_child"
            elif "disab" in first_need:
                mapped = "disability"

            st.session_state.pending_category_intent = mapped
            st.session_state.pop("finder_answers", None)

    # Step index initialization
    if "questionnaire_step" not in st.session_state:
        st.session_state.questionnaire_step = 1 if "intent" in answers else 0

    if "validation_error" not in st.session_state:
        st.session_state.validation_error = None

    # Resolve active question groups dynamically
    active_groups = questionnaire_engine.get_active_groups(answers)
    current_step = min(st.session_state.questionnaire_step, len(active_groups) - 1)
    current_step = max(0, current_step)
    st.session_state.questionnaire_step = current_step

    # Determine if viewport scroll to top is needed
    last_step = st.session_state.get("_last_questionnaire_step")
    explicit_scroll = st.session_state.get("_scroll_to_top_needed", False)
    step_changed = (last_step is not None and last_step != current_step)
    initial_entry = (last_step is None)
    should_scroll = explicit_scroll or step_changed or initial_entry

    # Center card container with anchor element for viewport positioning
    st.markdown(
        """
        <div id="questionnaire-top" style="max-width: 720px; margin: 0 auto; position: relative;">
            <div id="questionnaire-top-anchor" style="position: absolute; top: -20px; left: 0; height: 1px; width: 1px; opacity: 0; pointer-events: none;"></div>
        """,
        unsafe_allow_html=True,
    )

    # Render autofill dialog if there is a pending category intent
    pending_intent = st.session_state.get("pending_category_intent")
    if pending_intent:
        if lang == "hi":
            _autofill_dialog_hi(pending_intent)
        else:
            _autofill_dialog_en(pending_intent)

    # -----------------------------------------------------------------
    # Step 0: Goal / Intent Selection Screen
    # -----------------------------------------------------------------
    if current_step == 0:
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 2rem;">
                <div class="hero-tag-pill">
                    <span>✓</span>
                    <span>{"अनुकूली क्षेत्र-आधारित पात्रता प्रणाली" if lang == "hi" else "Sector-Aware Eligibility Engine"}</span>
                </div>
                <h1 style="color: #0F172A; font-size: 2.2rem; font-weight: 800; margin: 8px 0 10px 0; letter-spacing: -0.02em;">
                    {"आप किस प्रकार की योजना तलाश रहे हैं?" if lang == "hi" else "What are you looking for?"}
                </h1>
                <p style="color: #64748B; font-size: 1.05rem; max-width: 580px; margin: 0 auto; line-height: 1.5;">
                    {"अपना मुख्य उद्देश्य चुनें ताकि हम केवल उसी क्षेत्र से संबंधित प्रासंगिक प्रश्न पूछें — कोई अनावश्यक फॉर्म नहीं।" if lang == "hi" else "Select your primary goal so we only ask questions needed for matching schemes — no irrelevant questions."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        intent_field = active_groups[0].fields[0]
        st.markdown("<div class='intent-grid-container'>", unsafe_allow_html=True)
        cols = st.columns(2, gap="medium")
        for idx, opt in enumerate(intent_field.options):
            label = opt.label_hi if lang == "hi" else opt.label_en
            desc = opt.description_hi if lang == "hi" else opt.description_en
            with cols[idx % 2]:
                st.markdown(
                    f"""
                    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.1rem; margin-bottom: 0.85rem; min-height: 115px; display: flex; flex-direction: column; justify-content: space-between;">
                        <div>
                            <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; display: flex; align-items: center; gap: 8px;">
                                <span>{opt.icon}</span>
                                <span>{label}</span>
                            </div>
                            <div style="font-size: 0.82rem; color: #64748B; margin-top: 4px; line-height: 1.35;">
                                {desc or ''}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    ("चुनें →" if lang == "hi" else "Select →"),
                    key=f"intent_pick_{opt.key}",
                    type="primary" if answers.get("intent") == opt.key else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.pending_category_intent = opt.key
                    if lang == "hi":
                        _autofill_dialog_hi(opt.key)
                    else:
                        _autofill_dialog_en(opt.key)
        st.markdown("</div>", unsafe_allow_html=True)

        if should_scroll:
            st.session_state["_scroll_to_top_needed"] = False
            st.session_state["_last_questionnaire_step"] = 0
            inject_scroll_to_top(anchor_id="questionnaire-top")

        st.markdown("</div>", unsafe_allow_html=True)
        return

    # -----------------------------------------------------------------
    # Step 1+: Active Question Groups (Grouped Cards)
    # -----------------------------------------------------------------
    current_group = active_groups[current_step]
    total_steps = len(active_groups) - 1  # excluding intent selection step
    display_step = current_step

    # Header with dynamic group progress, autofill button, and change-goal button
    col_prog, col_autofill, col_reset = st.columns([2.5, 1.2, 1.3])
    with col_prog:
        st.markdown(
            f"""
            <div style="font-size: 0.8rem; font-weight: 700; color: #1E3A8A; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">
                {"चरण" if lang == "hi" else "Step"} {display_step} of {total_steps} — {"विवरण" if lang == "hi" else "Details"}
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_autofill:
        if st.button("⚡ " + ("ऑटो फिल" if lang == "hi" else "Auto Fill"), key="step_autofill_btn"):
            cat_key = answers.get("intent") or "education"
            has_profile, prof = get_saved_profile_for_autofill()
            if not st.session_state.get("is_authenticated", False):
                st.session_state.pending_category_intent = cat_key
                st.session_state["autofill_prompt_active"] = cat_key
                st.session_state["autofill_prompt_type"] = "not_signed_in"
                st.rerun()
            elif not has_profile:
                st.session_state.pending_category_intent = cat_key
                st.session_state["autofill_prompt_active"] = cat_key
                st.session_state["autofill_prompt_type"] = "incomplete_profile"
                st.rerun()
            else:
                apply_profile_to_answers(prof, answers, overwrite=False)
                st.session_state.fill_mode = "autofill"
                st.toast("Profile details applied to unfilled fields!")
                st.rerun()
    with col_reset:
        if st.button("🔄 " + ("उद्देश्य बदलें" if lang == "hi" else "Change Goal"), key="change_intent_btn"):
            reset_eligibility_session()
            st.rerun()

    progress_val = display_step / float(max(1, total_steps))
    st.progress(progress_val)

    # Active Group Card Header
    g_title = current_group.title_hi if lang == "hi" else current_group.title_en
    g_sub = current_group.subtitle_hi if lang == "hi" else current_group.subtitle_en

    # Card Container
    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #E5E7EB; border-radius: 16px; padding: 1.75rem 2rem 1.25rem 2rem; margin-top: 1rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <h2 style="color: #0F172A; font-size: 1.45rem; font-weight: 800; margin: 0 0 6px 0; letter-spacing: -0.015em;">
                {g_title}
            </h2>
            <p style="color: #64748B; font-size: 0.92rem; margin: 0 0 1.25rem 0; line-height: 1.5;">
                {g_sub}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Validation Error Banner if present
    if st.session_state.get("validation_error"):
        st.markdown(
            f"""
            <div style="background: #FEF2F2; border: 1px solid #FCA5A5; color: #991B1B; padding: 0.85rem 1.15rem; border-radius: 10px; font-size: 0.88rem; font-weight: 600; margin-bottom: 1.25rem;">
                ⚠️ {st.session_state.validation_error}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Render All Fields Belonging to Current Step Group
    for f in current_group.fields:
        if f.condition is not None and not f.condition(answers):
            continue

        widget_key = f"field_{f.id}"
        saved_val = answers.get(f.id)
        f_label = f.label_hi if lang == "hi" else f.label_en
        f_help = f.help_hi if lang == "hi" else f.help_en
        placeholder = f.placeholder_hi if lang == "hi" else f.placeholder_en

        # Render field label & helper text
        st.markdown(
            f"""
            <div style="margin-top: 1.1rem; margin-bottom: 0.35rem;">
                <label style="font-size: 0.95rem; font-weight: 700; color: #0F172A;">
                    {f_label}{' <span style="color: #DC2626;">*</span>' if f.required else ''}
                </label>
                {f'<div style="font-size: 0.8rem; color: #64748B; margin-top: 2px;">{f_help}</div>' if f_help else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Render specific widget control
        if f.widget_type == "select":
            opt_keys = [o.key for o in f.options]
            opt_labels = {o.key: (o.label_hi if lang == "hi" else o.label_en) for o in f.options}
            idx = opt_keys.index(saved_val) if (saved_val in opt_keys) else None
            chosen = st.selectbox(
                f_label,
                options=opt_keys,
                index=idx,
                placeholder=placeholder or "Select an option...",
                format_func=lambda k: opt_labels.get(k, k),
                key=widget_key,
                label_visibility="collapsed",
            )
            if chosen is not None:
                answers[f.id] = chosen
                if st.session_state.get("validation_error"):
                    st.session_state.validation_error = None

        elif f.widget_type == "radio":
            opt_keys = [o.key for o in f.options]
            opt_labels = {o.key: (o.label_hi if lang == "hi" else o.label_en) for o in f.options}
            idx = opt_keys.index(saved_val) if (saved_val in opt_keys) else None
            chosen = st.radio(
                f_label,
                options=opt_keys,
                index=idx,
                format_func=lambda k: opt_labels.get(k, k),
                key=widget_key,
                label_visibility="collapsed",
            )
            if chosen is not None:
                answers[f.id] = chosen
                if st.session_state.get("validation_error"):
                    st.session_state.validation_error = None

        elif f.widget_type == "number":
            num_val = float(saved_val) if (saved_val is not None and saved_val != "") else None
            chosen_num = st.number_input(
                f_label,
                min_value=float(f.min_value or 0.0),
                max_value=float(f.max_value or 10000000.0),
                step=float(f.step_value or 1.0),
                value=num_val,
                placeholder=placeholder,
                key=widget_key,
                label_visibility="collapsed",
            )
            if chosen_num is not None:
                answers[f.id] = chosen_num
                if st.session_state.get("validation_error"):
                    st.session_state.validation_error = None

        elif f.widget_type == "text":
            str_val = str(saved_val) if saved_val is not None else ""
            chosen_txt = st.text_input(
                f_label,
                value=str_val,
                placeholder=placeholder,
                key=widget_key,
                label_visibility="collapsed",
            )
            if chosen_txt is not None:
                answers[f.id] = chosen_txt.strip()
                if st.session_state.get("validation_error"):
                    st.session_state.validation_error = None

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Navigation Buttons: Back and Continue
    st.markdown("<div class='questionnaire-nav-container'>", unsafe_allow_html=True)
    is_last = (current_step == len(active_groups) - 1)
    col_back, col_spacer, col_next = st.columns([1.2, 2, 1.8], gap="small")

    with col_back:
        if st.button("← " + ("पीछे" if lang == "hi" else "Back"), use_container_width=True):
            st.session_state.validation_error = None
            st.session_state.questionnaire_step = max(0, current_step - 1)
            st.session_state["_scroll_to_top_needed"] = True
            st.rerun()

    with col_next:
        next_label = ("योजनाएं खोजें →" if lang == "hi" else "Find My Schemes →") if is_last else ("आगे बढ़ें →" if lang == "hi" else "Continue →")
        if st.button(next_label, type="primary", use_container_width=True, key="grouped_continue_btn"):
            # Sync any live widget values from session state before validating
            for f in current_group.fields:
                w_key = f"field_{f.id}"
                if w_key in st.session_state and st.session_state[w_key] is not None:
                    answers[f.id] = st.session_state[w_key]

            # Validate entire current group
            is_valid, err_msg = questionnaire_engine.validate_group(current_group, answers, lang=lang)

            if not is_valid:
                st.session_state.validation_error = err_msg
                st.session_state["_scroll_to_top_needed"] = True
                st.rerun()
            else:
                st.session_state.validation_error = None

                if not is_last:
                    st.session_state.questionnaire_step += 1
                    st.session_state["_scroll_to_top_needed"] = True
                    st.rerun()
                else:
                    # Final Submission: build normalized profile payload
                    with st.spinner("Evaluating matching government schemes..."):
                        payload = questionnaire_engine.build_profile_payload(answers)
                        st.session_state["eligibility_profile"] = payload

                        res = api_client.match_schemes(payload)
                        if res["ok"]:
                            st.session_state.match_results = res["data"]
                            st.session_state.matched_profile = payload
                            st.session_state["_scroll_to_top_needed"] = True
                            navigate_to("results")
                        else:
                            st.session_state.validation_error = f"API Error: {res.get('error', 'Unable to evaluate schemes')}"
                            st.session_state["_scroll_to_top_needed"] = True
                            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if should_scroll:
        st.session_state["_scroll_to_top_needed"] = False
        st.session_state["_last_questionnaire_step"] = current_step
        inject_scroll_to_top(anchor_id="questionnaire-top")

    st.markdown("</div>", unsafe_allow_html=True)
