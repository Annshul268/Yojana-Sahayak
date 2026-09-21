"""Eligibility breakdown component."""

from typing import Any, Callable, Dict, Optional
import streamlit as st
from frontend.utils.i18n import t


def render_eligibility_card(
    match: Dict[str, Any],
    on_explain: Optional[Callable[[Dict[str, Any]], None]] = None,
    on_view_details: Optional[Callable[[str], None]] = None,
) -> None:
    """Renders a visual breakdown of deterministic match criteria."""
    status = match.get("status", "potentially_eligible")
    score = match.get("score", 70)
    scheme_name = match.get("scheme_name", "")
    slug = match.get("slug", "")
    matched_rules = match.get("matched_rules", [])
    failed_rules = match.get("failed_rules", [])
    missing_info = match.get("missing_information", [])

    status_color = "#38A169" if status == "eligible" else ("#D69E2E" if status == "potentially_eligible" else "#E53E3E")
    status_label = t(f"status_{status}", status.replace("_", " ").title())

    st.markdown(
        f"""
        <div style="border: 2px solid {status_color}; border-radius: 8px; background: white; padding: 1.25rem; margin-bottom: 1.2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h3 style="margin: 0; color: #1A365D; font-size: 1.2rem;">{scheme_name}</h3>
                <span style="background: {status_color}22; color: {status_color}; border: 1px solid {status_color}; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 0.85rem;">
                    {status_label} ({score}%)
                </span>
            </div>
            <p style="color: #718096; font-size: 0.88rem; margin-bottom: 12px;">Ministry: {match.get('ministry', 'Government of India')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        if matched_rules:
            st.markdown("##### ✅ Matched Criteria")
            for r in matched_rules:
                st.markdown(f"- **{r.get('rule_name', '').title()}**: {r.get('reason', '')}")
        if failed_rules:
            st.markdown("##### ❌ Disqualifying Criteria")
            for r in failed_rules:
                st.markdown(f"- **{r.get('rule_name', '').title()}**: {r.get('reason', '')}")

    with col2:
        if missing_info:
            st.markdown("##### ⚠️ Information Needed to Confirm")
            for m in missing_info:
                st.markdown(f"- **{m.get('field', '').title()}**: {m.get('reason', '')}")

    col_b1, col_b2, col_b3 = st.columns([3, 3, 3])
    with col_b1:
        if st.button("🤖 Explain My Eligibility", key=f"btn_expl_{slug}", use_container_width=True):
            if on_explain:
                on_explain(match)
    with col_b2:
        if st.button("📋 Scheme Details", key=f"btn_vd_{slug}", use_container_width=True):
            if on_view_details:
                on_view_details(slug)
    with col_b3:
        st.link_button("🔗 Official Portal", match.get("official_url", "#"), use_container_width=True)

    st.markdown("<hr style='margin: 10px 0 16px 0; border: none; border-top: 1px dashed #E2E8F0;' />", unsafe_allow_html=True)
