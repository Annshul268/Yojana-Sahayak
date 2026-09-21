"""Scheme Card UI component for displaying government schemes."""

from typing import Any, Callable, Dict, Optional
import streamlit as st
from frontend.utils.i18n import get_current_language, t


def render_scheme_card(
    scheme: Dict[str, Any],
    on_details: Optional[Callable[[str], None]] = None,
    on_save: Optional[Callable[[str], None]] = None,
    is_saved: bool = False,
    score: Optional[int] = None,
    status: Optional[str] = None,
) -> None:
    """Renders a card for an individual welfare scheme."""
    lang = get_current_language()
    name = scheme.get("name_hi") if (lang == "hi" and scheme.get("name_hi")) else scheme.get("name", "")
    desc = scheme.get("description_hi") if (lang == "hi" and scheme.get("description_hi")) else scheme.get("description", "")
    category = scheme.get("category", "General")
    ministry = scheme.get("ministry", "Government of India")
    official_url = scheme.get("official_url", "#")
    slug = scheme.get("slug", "")

    # Status Pill style
    status_pill = ""
    if status:
        if status == "eligible":
            status_pill = "<span style='background: #C6F6D5; color: #22543D; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 0.8rem;'>✅ Eligible</span>"
        elif status == "potentially_eligible":
            status_pill = "<span style='background: #FEFCBF; color: #744210; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 0.8rem;'>⚠️ Potentially Eligible</span>"
        else:
            status_pill = "<span style='background: #FED7D7; color: #742A2A; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 0.8rem;'>❌ Not Eligible</span>"

    score_badge = ""
    if score is not None:
        score_badge = f"<span style='background: #EBF8FF; color: #2B6CB0; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 0.8rem;'>Match: {score}%</span>"

    with st.container():
        st.markdown(
            f"""
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                    <div>
                        <span style="background: #EDF2F7; color: #4A5568; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">{category}</span>
                        <span style="color: #A0AEC0; font-size: 0.8rem; margin: 0 6px;">•</span>
                        <span style="color: #718096; font-size: 0.78rem;">{ministry}</span>
                    </div>
                    <div>
                        {score_badge} {status_pill}
                    </div>
                </div>
                <h4 style="margin: 6px 0 8px 0; color: #1A365D; font-weight: 700; font-size: 1.15rem;">
                    {name}
                </h4>
                <p style="color: #4A5568; font-size: 0.92rem; line-height: 1.5; margin-bottom: 12px;">
                    {desc}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_act1, col_act2, col_act3, col_space = st.columns([2, 2, 3, 3])
        with col_act1:
            if st.button(t("btn_details", "View Details"), key=f"btn_det_{slug}", use_container_width=True):
                if on_details:
                    on_details(slug)
        with col_act2:
            save_label = t("btn_saved", "Saved") if is_saved else t("btn_save", "Bookmark")
            if st.button(f"{'⭐' if is_saved else '☆'} {save_label}", key=f"btn_save_{slug}", use_container_width=True):
                if on_save:
                    on_save(scheme.get("id", slug))
        with col_act3:
            st.link_button(f"🔗 {t('btn_official_portal', 'Official Portal')}", official_url, use_container_width=True)
