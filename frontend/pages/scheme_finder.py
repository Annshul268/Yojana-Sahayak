"""Intent-First Dynamic Eligibility Questionnaire with Robust State & Validation."""

from typing import Callable
import streamlit as st
from frontend.services.api_client import api_client
from frontend.services.questionnaire_engine import INDIAN_STATES, questionnaire_engine
from frontend.utils.i18n import get_current_language

OCCUPATION_OPTIONS = [
    ("student", "🎓 Student", "विद्यार्थी"),
    ("farmer", "🌾 Farmer / Agri", "किसान"),
    ("self-employed", "💼 Self-Employed / Business", "स्वरोजगार"),
    ("salaried", "🏢 Salaried Employee", "नौकरीपेशा"),
    ("street vendor", "🛒 Street Vendor / Artisan", "रेहड़ी-पटरी / कारीगर"),
    ("unemployed", "🔍 Looking for Work", "बेरोजगार"),
    ("retired", "👴 Senior / Retired", "वरिष्ठ नागरिक"),
    ("other", "✨ Other", "अन्य"),
]


def render_scheme_finder(navigate_to: Callable[[str], None]) -> None:
    lang = get_current_language()

    # 1. Initialize Single Canonical Answer Store
    if "eligibility_answers" not in st.session_state:
        st.session_state.eligibility_answers = {}

    # Alias for backward-compatibility
    st.session_state.adaptive_answers = st.session_state.eligibility_answers

    # Check if arrived from home category chip
    if "finder_answers" in st.session_state and "needs" in st.session_state.finder_answers:
        home_needs = st.session_state.finder_answers.get("needs", [])
        if home_needs and "intent" not in st.session_state.eligibility_answers:
            first_need = home_needs[0].lower()
            if "education" in first_need or "scholarship" in first_need:
                st.session_state.eligibility_answers["intent"] = "education"
            elif "business" in first_need or "loan" in first_need:
                st.session_state.eligibility_answers["intent"] = "business"
            elif "agri" in first_need:
                st.session_state.eligibility_answers["intent"] = "agriculture"
            elif "job" in first_need or "employ" in first_need:
                st.session_state.eligibility_answers["intent"] = "jobs"
            elif "skill" in first_need:
                st.session_state.eligibility_answers["intent"] = "skills"
            elif "housing" in first_need:
                st.session_state.eligibility_answers["intent"] = "housing"
            elif "health" in first_need:
                st.session_state.eligibility_answers["intent"] = "healthcare"
            elif "pension" in first_need:
                st.session_state.eligibility_answers["intent"] = "pension"
            elif "women" in first_need or "child" in first_need:
                st.session_state.eligibility_answers["intent"] = "women_child"
            elif "disab" in first_need:
                st.session_state.eligibility_answers["intent"] = "disability"

    # Step index initialization
    if "questionnaire_step" not in st.session_state:
        st.session_state.questionnaire_step = 1 if "intent" in st.session_state.eligibility_answers else 0

    if "validation_error" not in st.session_state:
        st.session_state.validation_error = None

    answers = st.session_state.eligibility_answers

    # Resolve active questions dynamically
    active_questions = questionnaire_engine.get_active_questions(answers)
    current_step = min(st.session_state.questionnaire_step, len(active_questions) - 1)
    current_step = max(0, current_step)
    st.session_state.questionnaire_step = current_step

    # Center card container
    st.markdown("<div style='max-width: 680px; margin: 0 auto;'>", unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # Step 0: Intent Selection Screen ("What are you looking for?")
    # -----------------------------------------------------------------
    if current_step == 0:
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 2rem;">
                <div class="hero-tag-pill">
                    <span>✓</span>
                    <span>{"अनुकूली पात्रता प्रणाली" if lang == "hi" else "Adaptive Eligibility Engine"}</span>
                </div>
                <h1 style="color: #0F172A; font-size: 2.2rem; font-weight: 800; margin: 8px 0 10px 0; letter-spacing: -0.02em;">
                    {"आप किस प्रकार की योजना तलाश रहे हैं?" if lang == "hi" else "What are you looking for?"}
                </h1>
                <p style="color: #64748B; font-size: 1.05rem; max-width: 540px; margin: 0 auto;">
                    {"अपना मुख्य उद्देश्य चुनें ताकि हम केवल वही प्रश्न पूछें जो आपकी चुनी हुई योजनाओं के लिए आवश्यक हैं।" if lang == "hi" else "Select your primary goal so we only ask questions needed for matching schemes — no unnecessary forms."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        intent_q = active_questions[0]
        cols = st.columns(2, gap="medium")
        for idx, opt in enumerate(intent_q.options):
            label = opt.label_hi if lang == "hi" else opt.label_en
            desc = opt.description_hi if lang == "hi" else opt.description_en
            with cols[idx % 2]:
                st.markdown(
                    f"""
                    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.1rem; margin-bottom: 0.85rem; height: 115px; display: flex; flex-direction: column; justify-content: space-between;">
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
                    answers["intent"] = opt.key
                    st.session_state.validation_error = None
                    # Clean any stale sub-answers from a previous intent
                    st.session_state.eligibility_answers = questionnaire_engine.clean_stale_answers(answers)
                    st.session_state.questionnaire_step = 1
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        return

    # -----------------------------------------------------------------
    # Step 1+: Active Questions
    # -----------------------------------------------------------------
    current_q = active_questions[current_step]
    total_steps = len(active_questions) - 1  # excluding intent step from count
    display_step = current_step

    # Header with dynamic progress and change-goal button
    col_prog, col_reset = st.columns([3, 1.2])
    with col_prog:
        st.markdown(
            f"""
            <div style="font-size: 0.8rem; font-weight: 700; color: #1E3A8A; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">
                {"प्रश्न" if lang == "hi" else "Question"} {display_step} of {total_steps}
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_reset:
        if st.button("🔄 " + ("उद्देश्य बदलें" if lang == "hi" else "Change Goal"), key="change_intent_btn"):
            st.session_state.validation_error = None
            st.session_state.questionnaire_step = 0
            st.rerun()

    progress_val = display_step / float(max(1, total_steps))
    st.progress(progress_val)

    # Active Question Card
    q_title = current_q.title_hi if lang == "hi" else current_q.title_en
    q_sub = current_q.subtitle_hi if lang == "hi" else current_q.subtitle_en

    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #E5E7EB; border-radius: 16px; padding: 2rem 2.25rem 1.5rem 2.25rem; margin-top: 1rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <h2 style="color: #0F172A; font-size: 1.45rem; font-weight: 800; margin: 0 0 6px 0; letter-spacing: -0.015em;">
                {q_title}
            </h2>
            <p style="color: #64748B; font-size: 0.92rem; margin: 0 0 1.25rem 0; line-height: 1.5;">
                {q_sub}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Widget Rendering with Stable Key & Canonical Synchronization
    widget_key = f"eligibility_{current_q.id}"
    saved_val = answers.get(current_q.id)

    if current_q.widget_type == "select":
        opt_keys = [o.key for o in current_q.options]
        opt_labels = {o.key: (o.label_hi if lang == "hi" else o.label_en) for o in current_q.options}
        placeholder = current_q.placeholder_hi if lang == "hi" else current_q.placeholder_en

        idx = opt_keys.index(saved_val) if (saved_val in opt_keys) else None
        chosen = st.selectbox(
            q_title,
            options=opt_keys,
            index=idx,
            placeholder=placeholder or "Select an option...",
            format_func=lambda k: opt_labels.get(k, k),
            key=widget_key,
            label_visibility="collapsed",
        )
        if chosen is not None:
            answers[current_q.id] = chosen
            # Clear validation error on change
            if st.session_state.get("validation_error"):
                st.session_state.validation_error = None

    elif current_q.widget_type == "radio":
        opt_keys = [o.key for o in current_q.options]
        opt_labels = {o.key: (o.label_hi if lang == "hi" else o.label_en) for o in current_q.options}

        idx = opt_keys.index(saved_val) if (saved_val in opt_keys) else None
        chosen = st.radio(
            q_title,
            options=opt_keys,
            index=idx,
            format_func=lambda k: opt_labels.get(k, k),
            key=widget_key,
            label_visibility="collapsed",
        )
        if chosen is not None:
            answers[current_q.id] = chosen
            if st.session_state.get("validation_error"):
                st.session_state.validation_error = None

    elif current_q.widget_type == "number":
        placeholder = current_q.placeholder_hi if lang == "hi" else current_q.placeholder_en
        val = float(saved_val) if (saved_val is not None and saved_val != "") else None

        chosen = st.number_input(
            q_title,
            min_value=float(current_q.min_value or 0.0),
            max_value=float(current_q.max_value or 10000000.0),
            step=float(current_q.step_value or 1.0),
            value=val,
            placeholder=placeholder,
            key=widget_key,
            label_visibility="collapsed",
        )
        if chosen is not None:
            answers[current_q.id] = chosen
            if st.session_state.get("validation_error"):
                st.session_state.validation_error = None

    # Minimalist Validation Message (Section 31)
    if st.session_state.get("validation_error"):
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; background: #FEF2F2; border: 1px solid #FCA5A5; border-radius: 8px; padding: 10px 14px; margin-top: 10px; margin-bottom: 10px;">
                <span style="font-size: 1rem;">⚠️</span>
                <span style="color: #B91C1C; font-size: 0.88rem; font-weight: 500;">
                    {st.session_state["validation_error"]}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # Navigation Buttons: Back and Continue
    is_last = (current_step == len(active_questions) - 1)
    col_back, col_spacer, col_next = st.columns([1.2, 2, 1.8], gap="small")

    with col_back:
        if st.button("← " + ("पीछे" if lang == "hi" else "Back"), use_container_width=True):
            st.session_state.validation_error = None
            st.session_state.questionnaire_step = max(0, current_step - 1)
            st.rerun()

    with col_next:
        next_label = ("योजनाएं खोजें →" if lang == "hi" else "Find My Schemes →") if is_last else ("आगे बढ़ें →" if lang == "hi" else "Continue →")
        if st.button(next_label, type="primary", use_container_width=True, key="adaptive_next_btn"):
            # Step 1: Read current value with fallback to widget session key
            current_ans = answers.get(current_q.id)
            if (current_ans is None or current_ans == "") and widget_key in st.session_state:
                w_val = st.session_state.get(widget_key)
                if w_val is not None:
                    current_ans = w_val
                    answers[current_q.id] = w_val

            # Step 2: Validate against question definition
            is_valid, err_msg = questionnaire_engine.validate_answer(current_q, current_ans, lang=lang)

            if not is_valid:
                # DO NOT ADVANCE! Stay on the same question with error message
                st.session_state.validation_error = err_msg
                st.rerun()
            else:
                # VALID! Clear error and clean stale answers
                st.session_state.validation_error = None
                st.session_state.eligibility_answers = questionnaire_engine.clean_stale_answers(answers)

                if not is_last:
                    st.session_state.questionnaire_step += 1
                    st.rerun()
                else:
                    # Final Submission: validate all active questions before sending
                    all_valid = True
                    for q in active_questions:
                        q_val = answers.get(q.id)
                        q_ok, q_err = questionnaire_engine.validate_answer(q, q_val, lang=lang)
                        if not q_ok:
                            st.session_state.validation_error = q_err
                            all_valid = False
                            break

                    if not all_valid:
                        st.rerun()

                    # Send to FastAPI Matching Pipeline
                    with st.spinner("Evaluating matching government schemes..."):
                        payload = questionnaire_engine.build_profile_payload(answers)
                        res = api_client.match_schemes(payload)
                        if res["ok"]:
                            st.session_state.match_results = res["data"]
                            st.session_state.matched_profile = payload
                            navigate_to("results")
                        else:
                            st.error("Could not complete matching right now. Please verify backend connection.")

    st.markdown("</div>", unsafe_allow_html=True)
