"""Clean, focused Scheme Details view matching the civic design system."""

from typing import Callable
import streamlit as st
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language
from frontend.utils.ui import inject_scheme_details_scroll_to_top


def render_scheme_details(navigate_to: Callable[[str], None]) -> None:
    slug = st.session_state.get("selected_scheme_slug")
    if not slug:
        st.warning("No scheme selected.")
        if st.button("← Back to Directory"):
            navigate_to("schemes")
        return

    # Check whether viewport scroll-to-top is needed on this navigation
    cur_slug = slug
    last_viewed_slug = st.session_state.get("_last_viewed_scheme_slug")
    last_page = st.session_state.get("_last_rendered_page", "")
    explicit_scroll = st.session_state.pop("_scheme_scroll_to_top", False)

    should_scroll = (
        explicit_scroll
        or (last_page != "scheme_details")
        or (last_viewed_slug != cur_slug)
        or ("_scheme_view_initialized" not in st.session_state)
    )

    st.session_state["_last_viewed_scheme_slug"] = cur_slug
    st.session_state["_last_rendered_page"] = "scheme_details"
    st.session_state["_scheme_view_initialized"] = True

    # Top anchor element for instant scrolling
    st.markdown(
        '<div id="scheme-detail-top" style="position: absolute; top: 0; left: 0; width: 1px; height: 1px; margin: 0; padding: 0; opacity: 0; pointer-events: none;"></div>',
        unsafe_allow_html=True,
    )

    # Back Link button
    col_bk, _ = st.columns([2, 8])
    with col_bk:
        if st.button("← " + ("वापस" if st.session_state.get("lang") == "hi" else "Back"), key="scheme_det_back_btn"):
            # Return to results if results exist, else schemes directory
            if st.session_state.get("match_results"):
                navigate_to("results")
            else:
                navigate_to("schemes")

    # Fetch scheme data
    res = api_client.get_scheme(slug)
    if not res["ok"]:
        st.error("Could not load scheme details right now. Please try again.")
        return

    scheme = res["data"]
    lang = get_current_language()

    name = scheme.get("name_hi") if (lang == "hi" and scheme.get("name_hi")) else scheme.get("name", "")
    desc = scheme.get("description_hi") if (lang == "hi" and scheme.get("description_hi")) else scheme.get("description", "")
    category = scheme.get("category", "")
    ministry = scheme.get("ministry", "Government of India")
    official_url = scheme.get("official_url", "#")
    user_id = st.session_state.get("user_id", "citizen_user_1")

    # Scheme Title & Ministry Header
    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #E5E7EB; border-radius: 16px; padding: 2rem; margin-top: 10px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <span class="category-badge-pill">{category}</span>
                <span style="font-size: 0.85rem; color: #64748B;">• {ministry}</span>
            </div>
            <h1 style="color: #0F172A; font-size: 2.1rem; font-weight: 800; margin: 6px 0 12px 0; line-height: 1.25;">
                {name}
            </h1>
            <p style="color: #475569; font-size: 1.05rem; line-height: 1.6; margin: 0;">
                {desc}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Key Benefits
    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #E5E7EB; border-radius: 14px; padding: 1.5rem; margin-bottom: 1.25rem;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 12px;">
                {"योजना के प्रमुख लाभ" if lang == "hi" else "Key Benefits & Financial Assistance"}
            </div>
        """,
        unsafe_allow_html=True,
    )
    benefits = scheme.get("benefits", [])
    if benefits:
        for b in benefits:
            st.markdown(f"- **{b}**")
    else:
        st.write("Direct financial or welfare assistance as notified by the Government of India.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Documents Required
    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #E5E7EB; border-radius: 14px; padding: 1.5rem; margin-bottom: 1.25rem;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 12px;">
                {"आवश्यक दस्तावेज" if lang == "hi" else "Documents Required to Apply"}
            </div>
        """,
        unsafe_allow_html=True,
    )
    docs = scheme.get("documents", [])
    if docs:
        d_col1, d_col2 = st.columns(2)
        for idx, d in enumerate(docs):
            with (d_col1 if idx % 2 == 0 else d_col2):
                st.markdown(f"• **{d}**")
    else:
        st.write("Standard citizen proofs: Aadhaar Card, Bank Account Details, and Mobile Number.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. How to Apply
    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #E5E7EB; border-radius: 14px; padding: 1.5rem; margin-bottom: 1.5rem;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 12px;">
                {"आवेदन करने की चरणबद्ध प्रक्रिया" if lang == "hi" else "Step-by-Step Application Process"}
            </div>
        """,
        unsafe_allow_html=True,
    )
    steps = scheme.get("application_steps", [])
    if steps:
        for idx, s in enumerate(steps, 1):
            st.markdown(f"**Step {idx}:** {s}")
    else:
        st.write(f"Visit the official portal at {official_url} to submit your online application.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 4. Primary Actions (Official Link & Add to Tracker)
    col_act1, col_act2 = st.columns(2, gap="medium")
    with col_act1:
        st.link_button(
            ("आधिकारिक वेबसाइट पर जाएं" if lang == "hi" else "Visit Official Government Portal"),
            official_url,
            type="primary",
            use_container_width=True,
        )
    with col_act2:
        is_already_added = api_client.is_in_applications(user_id=user_id, scheme_id=scheme["id"])
        just_added = st.session_state.get(f"just_added_{scheme['id']}", False)

        if is_already_added or just_added:
            col_b1, col_b2 = st.columns([1.1, 1], gap="small")
            with col_b1:
                badge_label = (
                    "आवेदनों में जोड़ा गया"
                    if lang == "hi"
                    else ("Added to My Applications" if just_added else "Already in My Applications")
                )
                st.button(badge_label, disabled=True, use_container_width=True, key=f"app_status_btn_{scheme['id']}")
            with col_b2:
                view_apps_label = "मेरे आवेदन" if lang == "hi" else "View My Applications"
                if st.button(view_apps_label, type="primary", use_container_width=True, key=f"view_apps_btn_{scheme['id']}"):
                    navigate_to("tracker")
        else:
            add_label = ("आवेदनों में जोड़ें" if lang == "hi" else "Add to My Applications")
            if st.button(add_label, use_container_width=True, key=f"add_app_btn_{scheme['id']}"):
                if not st.session_state.get("is_authenticated", False):
                    st.session_state.auth_redirect_target = "scheme_details"
                    st.toast("Please sign in to add to My Applications")
                    navigate_to("profile")
                else:
                    track_res = api_client.create_tracking(
                        user_id=user_id,
                        scheme_id=scheme["id"],
                        status="Saved",
                        notes=f"Added from {name}",
                    )
                    if track_res.get("ok"):
                        st.session_state[f"just_added_{scheme['id']}"] = True
                        st.toast("Added to My Applications")
                        st.rerun()
                    else:
                        st.error("Could not add to My Applications. Please try again.")

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    # 5. Embedded Grounded AI Assistant Drawer
    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #E5E7EB; border-radius: 14px; padding: 1.75rem;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span style="font-size: 1.25rem;">🤖</span>
                <h4 style="color: #0F172A; margin: 0; font-weight: 700;">
                    {"इस योजना के बारे में कोई प्रश्न है?" if lang == "hi" else "Have a question about this scheme?"}
                </h4>
            </div>
            <p style="color: #64748B; font-size: 0.9rem; margin: 0 0 16px 0;">
                {"आधिकारिक नियमों और तथ्यों पर आधारित तत्काल सहायता प्राप्त करें:" if lang == "hi" else "Ask anything and receive facts grounded strictly in official government scheme notifications:"}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    suggested_q = [
        "What documents do I need to apply?",
        "Who is eligible for this scheme?",
        "Explain key benefits in simple words",
    ]
    if lang == "hi":
        suggested_q = [
            "आवेदन के लिए कौन से दस्तावेज चाहिए?",
            "क्या मैं इस योजना के लिए पात्र हूँ?",
            "सरल हिंदी में मुख्य लाभ बताएं",
        ]

    chosen_query = None
    q_cols = st.columns(len(suggested_q), gap="small")
    for idx, sq in enumerate(suggested_q):
        with q_cols[idx]:
            if st.button(f"💬 {sq}", key=f"sq_btn_{idx}", use_container_width=True):
                chosen_query = f"{sq} regarding {name}"

    custom_q = st.text_input(
        "Ask Yojana Sahayak:",
        placeholder="e.g. Is there any fee or maximum income limit?",
        key="ai_custom_q_input",
        label_visibility="collapsed",
    )
    if st.button("Ask Assistant" if lang != "hi" else "पूछें", type="secondary", key="ai_submit_q_btn") and custom_q.strip():
        chosen_query = f"{custom_q} regarding {name}"

    if chosen_query:
        with st.spinner("Retrieving verified facts from official data..."):
            ai_res = api_client.ask_ai(question=chosen_query, language=lang)
            if ai_res["ok"]:
                st.markdown(
                    f"""
                    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1rem 1.25rem; margin-top: 12px;">
                        <div style="font-size: 0.85rem; font-weight: 700; color: #1E3A8A; margin-bottom: 6px;">💡 Official Answer:</div>
                        <div style="color: #1E293B; font-size: 0.95rem; line-height: 1.5;">{ai_res["data"]["answer"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.error("Unable to generate AI answer right now.")

    # Reset viewport scroll position strictly after page elements have completely rendered
    if should_scroll:
        inject_scheme_details_scroll_to_top(anchor_id="scheme-detail-top")
