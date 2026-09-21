"""Human-friendly scheme eligibility match card with structured reasons and AI explanation."""

from typing import Any, Callable, Dict, Optional
import streamlit as st
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language


def render_eligibility_card(
    match: Dict[str, Any],
    on_view_details: Optional[Callable[[str], None]] = None,
    on_save: Optional[Callable[[str], None]] = None,
    is_saved: bool = False,
) -> None:
    """Renders a sleek, human-first scheme match card without technical algorithmic scores."""
    lang = get_current_language()
    status = match.get("status", "potentially_eligible")
    scheme_name = match.get("scheme_name_hi") if (lang == "hi" and match.get("scheme_name_hi")) else match.get("scheme_name", "")
    slug = match.get("slug", "")
    scheme_id = match.get("scheme_id", slug)
    category = match.get("category", "")
    ministry = match.get("ministry", "")
    benefits = match.get("benefits", [])
    benefit_highlight = benefits[0] if benefits else ""
    matched_attrs = match.get("matched_attributes", []) or [r.get("reason", "") for r in match.get("matched_rules", [])]
    failed_conds = match.get("failed_conditions", []) or [r.get("reason", "") for r in match.get("failed_rules", [])]
    important_conds = match.get("important_conditions", [])
    missing_info = match.get("missing_information", [])
    reason = match.get("reason", "")
    official_url = match.get("official_url", "#")

    # Status Pill
    if status == "eligible":
        status_html = (
            '<span class="status-pill-eligible">✓ '
            + ("आप पात्र हो सकते हैं" if lang == "hi" else "Likely eligible based on your details")
            + "</span>"
        )
    elif status == "potentially_eligible":
        status_html = (
            '<span class="status-pill-potential">ℹ '
            + ("अतिरिक्त सत्यापन आवश्यक" if lang == "hi" else "Verification required")
            + "</span>"
        )
    else:
        status_html = (
            '<span style="background: #FEE2E2; color: #991B1B; font-size: 0.8rem; font-weight: 600; padding: 4px 10px; border-radius: 20px;">'
            + ("अपात्र" if lang == "hi" else "Criteria not matching")
            + "</span>"
        )

    # Clean Card container
    with st.container():
        st.markdown(
            f"""
            <div style="background: white; border: 1px solid #E5E7EB; border-radius: 14px; padding: 1.5rem; margin-bottom: 0.75rem; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="category-badge-pill">{category}</span>
                        <span style="font-size: 0.8rem; color: #94A3B8;">• {ministry}</span>
                    </div>
                    <div>{status_html}</div>
                </div>
                <h3 style="color: #0F172A; margin: 6px 0 8px 0; font-size: 1.25rem; font-weight: 700;">
                    {scheme_name}
                </h3>
                {f'<div style="display: inline-block; background: #FEF3C7; color: #92400E; font-size: 0.82rem; font-weight: 600; padding: 3px 10px; border-radius: 6px; margin-bottom: 10px;">🎁 {benefit_highlight}</div>' if benefit_highlight else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # "Why this matches" and "Important conditions" section
        if matched_attrs or missing_info or important_conds:
            reasons_html = []
            for a in matched_attrs[:3]:
                if a:
                    reasons_html.append(f"<div style='color: #047857; font-size: 0.86rem; margin-bottom: 3px;'>✓ {a}</div>")
            for m in missing_info[:2]:
                m_reason = m.get("reason") if isinstance(m, dict) else str(m)
                reasons_html.append(f"<div style='color: #B45309; font-size: 0.86rem; margin-bottom: 3px;'>ℹ Verification required: {m_reason}</div>")

            important_html = ""
            if important_conds:
                cond_bullets = "".join([f"<li style='margin-bottom: 2px;'>{c}</li>" for c in important_conds[:2]])
                important_html = f"""
                <div style="margin-top: 8px; padding-top: 6px; border-top: 1px dashed #E2E8F0; font-size: 0.82rem; color: #64748B;">
                    <strong>Important conditions:</strong>
                    <ul style="margin: 4px 0 0 16px; padding: 0;">{cond_bullets}</ul>
                </div>
                """

            st.markdown(
                f"""
                <div style="background: #F8FAFC; border: 1px solid #F1F5F9; border-radius: 10px; padding: 12px 14px; margin-top: -12px; margin-bottom: 12px;">
                    <div style="font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 6px;">
                        {"यह योजना आपके लिए क्यों उपयुक्त है:" if lang == "hi" else "Why this scheme matches your profile:"}
                    </div>
                    {''.join(reasons_html)}
                    {important_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Action Buttons row
        col_act1, col_act2, col_act3, col_ai = st.columns([1.5, 0.9, 1.4, 1.4], gap="small")
        with col_act1:
            if st.button(
                "योजना देखें →" if lang == "hi" else "View Scheme →",
                key=f"card_view_{slug}",
                type="primary",
                use_container_width=True,
            ):
                if on_view_details:
                    on_view_details(slug)

        with col_act2:
            save_lbl = "⭐ " + ("सहेजा" if lang == "hi" else "Saved") if is_saved else "☆ " + ("सहेजें" if lang == "hi" else "Save")
            if st.button(save_lbl, key=f"card_save_{slug}", use_container_width=True):
                if on_save:
                    on_save(scheme_id)

        with col_act3:
            st.link_button(
                "🔗 " + ("आधिकारिक पोर्टल" if lang == "hi" else "Official Portal"),
                official_url,
                use_container_width=True,
            )

        with col_ai:
            if st.button("💡 " + ("एआई व्याख्या" if lang == "hi" else "AI Explain"), key=f"card_ai_{slug}", use_container_width=True):
                st.session_state[f"show_ai_explain_{slug}"] = not st.session_state.get(f"show_ai_explain_{slug}", False)

        # Expandable Grounded AI Explanation
        if st.session_state.get(f"show_ai_explain_{slug}", False):
            with st.spinner("Generating grounded AI explanation..."):
                query = f"Explain in simple plain language why an applicant qualifies for {scheme_name} and what documents are required."
                ai_res = api_client.ask_ai(question=query, language=lang)
                if ai_res["ok"]:
                    st.markdown(
                        f"""
                        <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 10px; padding: 12px 14px; margin-top: 8px; margin-bottom: 12px;">
                            <div style="font-size: 0.82rem; font-weight: 700; color: #166534; margin-bottom: 4px;">
                                🤖 {"आधिकारिक तथ्यों पर आधारित एआई व्याख्या:" if lang == "hi" else "Grounded AI Explanation:"}
                            </div>
                            <div style="font-size: 0.9rem; color: #14532D; line-height: 1.5;">
                                {ai_res["data"]["answer"]}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
