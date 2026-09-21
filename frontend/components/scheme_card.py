"""Clean scheme card for directory browsing."""

from typing import Any, Callable, Dict, Optional
import streamlit as st
from frontend.utils.i18n import get_current_language


def render_scheme_card(
    scheme: Dict[str, Any],
    on_details: Optional[Callable[[str], None]] = None,
    on_save: Optional[Callable[[str], None]] = None,
    is_saved: bool = False,
) -> None:
    """Renders a visually clean, calm scheme card for browsing."""
    lang = get_current_language()
    name = scheme.get("name_hi") if (lang == "hi" and scheme.get("name_hi")) else scheme.get("name", "")
    desc = scheme.get("description_hi") if (lang == "hi" and scheme.get("description_hi")) else scheme.get("description", "")
    category = scheme.get("category", "General")
    ministry = scheme.get("ministry", "Government of India")
    slug = scheme.get("slug", "")
    scheme_id = scheme.get("id", slug)
    official_url = scheme.get("official_url", "#")
    benefits = scheme.get("benefits", [])
    benefit_highlight = benefits[0] if benefits else ""

    with st.container():
        st.markdown(
            f"""
            <div style="background: white; border: 1px solid #E5E7EB; border-radius: 14px; padding: 1.4rem; margin-bottom: 0.75rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="category-badge-pill">{category}</span>
                        <span style="font-size: 0.8rem; color: #94A3B8;">• {ministry}</span>
                    </div>
                    <span style="font-size: 0.78rem; color: #047857; font-weight: 600;">✓ Verified Scheme</span>
                </div>
                <h3 style="color: #0F172A; font-size: 1.2rem; font-weight: 700; margin: 4px 0 6px 0;">
                    {name}
                </h3>
                <p style="color: #64748B; font-size: 0.92rem; line-height: 1.5; margin-bottom: 10px;">
                    {desc[:170]}{'...' if len(desc) > 170 else ''}
                </p>
                {f'<div style="display: inline-block; background: #FEF3C7; color: #92400E; font-size: 0.8rem; font-weight: 600; padding: 3px 10px; border-radius: 6px; margin-bottom: 12px;">🎁 {benefit_highlight}</div>' if benefit_highlight else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1.5, 0.9, 1.4], gap="small")
        with col1:
            if st.button(
                "योजना देखें →" if lang == "hi" else "View Scheme →",
                key=f"dir_det_{slug}",
                type="primary",
                use_container_width=True,
            ):
                if on_details:
                    on_details(slug)
        with col2:
            save_label = "⭐ " + ("सहेजा" if lang == "hi" else "Saved") if is_saved else "☆ " + ("सहेजें" if lang == "hi" else "Save")
            if st.button(save_label, key=f"dir_save_{slug}", use_container_width=True):
                if on_save:
                    on_save(scheme_id)
        with col3:
            st.link_button(
                "🔗 " + ("आधिकारिक पोर्टल" if lang == "hi" else "Official Website"),
                official_url,
                use_container_width=True,
            )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
