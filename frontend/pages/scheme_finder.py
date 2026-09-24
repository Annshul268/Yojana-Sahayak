"""Sector-Aware Grouped Eligibility Questionnaire with Stable State & Validation."""

from typing import Callable
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


def render_scheme_finder(navigate_to: Callable[[str], None]) -> None:
    lang = get_current_language()

    # 1. Initialize Single Canonical Answer Store
    if "eligibility_answers" not in st.session_state:
        st.session_state.eligibility_answers = {}

    # Alias for backward-compatibility
    st.session_state.adaptive_answers = st.session_state.eligibility_answers
    answers = st.session_state.eligibility_answers

    # Check if arrived from home category chip
    if "finder_answers" in st.session_state and "needs" in st.session_state.finder_answers:
        home_needs = st.session_state.finder_answers.get("needs", [])
        if home_needs and "intent" not in answers:
            first_need = home_needs[0].lower()
            if "education" in first_need or "scholarship" in first_need:
                answers["intent"] = "education"
            elif "business" in first_need or "loan" in first_need:
                answers["intent"] = "business"
            elif "agri" in first_need:
                answers["intent"] = "agriculture"
            elif "intern" in first_need:
                answers["intent"] = "internships"
            elif "job" in first_need or "employ" in first_need:
                answers["intent"] = "jobs"
            elif "skill" in first_need:
                answers["intent"] = "skills"
            elif "housing" in first_need:
                answers["intent"] = "housing"
            elif "health" in first_need:
                answers["intent"] = "healthcare"
            elif "pension" in first_need:
                answers["intent"] = "pension"
            elif "women" in first_need or "child" in first_need:
                answers["intent"] = "women_child"
            elif "disab" in first_need:
                answers["intent"] = "disability"

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
        cols = st.columns(2, gap="medium")
        for idx, opt in enumerate(intent_field.options):
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
                    st.session_state.questionnaire_step = 1
                    st.session_state["_scroll_to_top_needed"] = True
                    st.rerun()

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

    # Header with dynamic group progress and change-goal button
    col_prog, col_reset = st.columns([3, 1.3])
    with col_prog:
        st.markdown(
            f"""
            <div style="font-size: 0.8rem; font-weight: 700; color: #1E3A8A; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">
                {"चरण" if lang == "hi" else "Step"} {display_step} of {total_steps} — {"विवरण" if lang == "hi" else "Details"}
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_reset:
        if st.button("🔄 " + ("उद्देश्य बदलें" if lang == "hi" else "Change Goal"), key="change_intent_btn"):
            st.session_state.validation_error = None
            st.session_state.questionnaire_step = 0
            st.session_state["_scroll_to_top_needed"] = True
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

    if should_scroll:
        st.session_state["_scroll_to_top_needed"] = False
        st.session_state["_last_questionnaire_step"] = current_step
        inject_scroll_to_top(anchor_id="questionnaire-top")

    st.markdown("</div>", unsafe_allow_html=True)
