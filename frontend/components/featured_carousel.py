"""Single-Scheme Featured Government Schemes responsive auto-scrolling carousel component.

Displays exactly ONE scheme card at a time with real photographic banner image,
smooth transitions, previous/next navigation arrows, indicator dots,
auto-scroll every 4.5 seconds, and direct synchronization between displayed scheme,
banner image, text, and navigation target.
"""

import time
from typing import Any, Callable, Dict, List, Optional
import streamlit as st

# Real high-resolution photographic banners for government sectors
DEFAULT_BANNER_IMAGES = {
    "pm-kisan": "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=700&q=80",
    "ayushman-bharat-pmjay": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=700&q=80",
    "up-post-matric-scholarship-obc": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=700&q=80",
    "pmay-gramin": "https://images.unsplash.com/photo-1518780664697-55e3ad937233?auto=format&fit=crop&w=700&q=80",
    "adip-scheme-disabled": "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?auto=format&fit=crop&w=700&q=80",
    "Agriculture & Rural Development": "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=700&q=80",
    "Healthcare": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=700&q=80",
    "Education & Learning": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=700&q=80",
    "Housing & Shelter": "https://images.unsplash.com/photo-1518780664697-55e3ad937233?auto=format&fit=crop&w=700&q=80",
    "Differently Abled Support": "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?auto=format&fit=crop&w=700&q=80",
    "Social Security & Pension": "https://images.unsplash.com/photo-1516307365426-bea591f05011?auto=format&fit=crop&w=700&q=80",
    "Business & Self Employment": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=700&q=80",
    "Employment & Skills": "https://images.unsplash.com/photo-1521737711867-e3b97375f902?auto=format&fit=crop&w=700&q=80",
    "Women & Child Development": "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?auto=format&fit=crop&w=700&q=80",
    "Financial Assistance": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=700&q=80",
}

FALLBACK_IMAGE = "https://images.unsplash.com/photo-1532375810709-75b1da00537c?auto=format&fit=crop&w=700&q=80"


def get_scheme_banner_image(category: str, slug: str, existing_url: str = None) -> str:
    """Returns a real, high-resolution photographic image URL for the scheme."""
    if existing_url and existing_url.startswith("http"):
        return existing_url
    if slug in DEFAULT_BANNER_IMAGES:
        return DEFAULT_BANNER_IMAGES[slug]
    if category in DEFAULT_BANNER_IMAGES:
        return DEFAULT_BANNER_IMAGES[category]
    return FALLBACK_IMAGE


@st.fragment(run_every=4.5)
def render_featured_carousel(
    schemes: List[Dict[str, Any]],
    lang: str = "en",
    navigate_to: Optional[Callable[[str], None]] = None,
) -> None:
    """Renders a single-scheme carousel showing exactly ONE card at a time with synchronized navigation."""
    if not schemes:
        return

    # Critical: Do not execute or render carousel if the user has navigated away from home
    if st.session_state.get("current_page", "home") != "home":
        return

    total = len(schemes)

    # Initialize index and timer
    if "featured_carousel_index" not in st.session_state:
        st.session_state.featured_carousel_index = 0

    current_idx = st.session_state.featured_carousel_index % total

    # Auto-scroll interval check
    now = time.time()
    last_tick = st.session_state.get("_carousel_last_tick")
    if last_tick is None:
        st.session_state["_carousel_last_tick"] = now
    elif now - last_tick >= 3.8:
        # Automatic tick: advance to next scheme
        current_idx = (current_idx + 1) % total
        st.session_state.featured_carousel_index = current_idx
        st.session_state["_carousel_last_tick"] = now

    s = schemes[current_idx]
    slug = s.get("slug", "")
    category = s.get("category", "General")
    level = s.get("level", "Central")
    states = s.get("states", ["ALL"])
    state_label = states[0] if (level != "Central" and states and "ALL" not in states) else ""

    banner_url = get_scheme_banner_image(category, slug, s.get("image_url"))

    name = s.get("name_hi") if (lang == "hi" and s.get("name_hi")) else s.get("name", "")
    desc = s.get("description_hi") if (lang == "hi" and s.get("description_hi")) else s.get("description", "")
    if len(desc) > 140:
        desc = desc[:137] + "..."

    view_btn_text = "योजना देखें →" if lang == "hi" else "View Scheme →"
    central_badge = "केंद्रीय योजना" if lang == "hi" else "Central Scheme"
    state_badge = "राज्य योजना" if lang == "hi" else "State Scheme"
    level_badge_text = central_badge if level == "Central" else (state_label or state_badge)

    official_url = (s.get("official_url") or s.get("url") or "").strip()
    has_official_url = bool(official_url and official_url.startswith("http"))
    image_href = official_url if has_official_url else "#"
    image_target = 'target="_blank" rel="noopener noreferrer"' if has_official_url else 'target="_self"'

    # Scoped styles for the featured carousel component
    st.markdown(
        """
        <style>
        .carousel-card-wrap {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08);
            overflow: hidden;
            width: 100%;
            margin-bottom: 0px;
        }
        .carousel-banner-anchor {
            display: block;
            width: 100%;
            height: 185px;
            overflow: hidden;
            background: #0F172A;
            position: relative;
            cursor: pointer;
            text-decoration: none;
        }
        .carousel-banner-anchor img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            transition: transform 0.35s ease;
        }
        .carousel-banner-anchor:hover img {
            transform: scale(1.05);
        }
        .carousel-external-pill {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(15, 23, 42, 0.82);
            backdrop-filter: blur(4px);
            color: #FFFFFF;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 9999px;
            border: 1px solid rgba(255, 255, 255, 0.25);
            display: flex;
            align-items: center;
            gap: 4px;
            pointer-events: none;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        }
        .carousel-body-box {
            padding: 16px 20px 10px 20px;
        }
        .carousel-badges-row {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 8px;
        }
        .carousel-badge-pill {
            font-size: 0.74rem;
            font-weight: 700;
            padding: 3px 9px;
            border-radius: 9999px;
            line-height: 1.2;
        }
        .carousel-badge-cat {
            background: #EFF6FF;
            color: #1D4ED8;
            border: 1px solid #DBEAFE;
        }
        .carousel-badge-lvl {
            background: #F8FAFC;
            color: #334155;
            border: 1px solid #E2E8F0;
        }
        .carousel-card-heading {
            font-size: 1.15rem;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.35;
            margin-bottom: 6px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            min-height: 2.7em;
            text-decoration: none;
        }
        .carousel-card-summary {
            font-size: 0.88rem;
            color: #64748B;
            line-height: 1.5;
            margin-bottom: 8px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .carousel-dots-cluster {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
            height: 38px;
        }
        .carousel-dot-marker {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #CBD5E1;
            transition: all 0.2s ease;
        }
        .carousel-dot-marker.active {
            width: 20px;
            border-radius: 9999px;
            background: #2563EB;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 1. Main Scheme Card Content (Banner Image linking to Official Government Website, Badges, Title, Description)
    card_html = f"""
    <div class="carousel-card-wrap">
        <a href="{image_href}" {image_target} class="carousel-banner-anchor" aria-label="Official Website: {name}" title="{official_url if has_official_url else name}">
            <img src="{banner_url}" alt="{name}" onerror="this.src='{FALLBACK_IMAGE}'" />
            {f'<div class="carousel-external-pill"><span>🌐 {"आधिकारिक वेबसाइट ↗" if lang == "hi" else "Official Website ↗"}</span></div>' if has_official_url else ''}
        </a>
        <div class="carousel-body-box">
            <div class="carousel-badges-row">
                <span class="carousel-badge-pill carousel-badge-cat">{category}</span>
                <span class="carousel-badge-pill carousel-badge-lvl">{level_badge_text}</span>
            </div>
            <div class="carousel-card-heading">{name}</div>
            <div class="carousel-card-summary">{desc}</div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    # 2. Controls & Actions Footer Row
    col_view, col_prev, col_dots, col_next = st.columns(
        [4.2, 1.2, 2.2, 1.2],
        gap="small",
        vertical_alignment="center",
    )

    with col_view:
        def on_view_scheme_click(slug_val=slug):
            st.session_state.selected_scheme_slug = slug_val
            st.session_state["scheme_navigation_source"] = "featured"
            st.session_state["_scheme_scroll_to_top"] = True
            if navigate_to:
                navigate_to("scheme_details")
            else:
                st.session_state.current_page = "scheme_details"
                st.rerun()

        if st.button(
            view_btn_text,
            key=f"feat_view_{current_idx}_{slug}",
            type="primary",
            use_container_width=True,
            on_click=on_view_scheme_click,
            args=(slug,),
        ):
            on_view_scheme_click(slug)

    with col_prev:
        if st.button("←", key=f"feat_prev_{current_idx}", use_container_width=True):
            st.session_state.featured_carousel_index = (current_idx - 1 + total) % total
            st.session_state["_carousel_last_tick"] = time.time()
            st.rerun(scope="fragment")

    with col_dots:
        dots_html = f"""
        <div class="carousel-dots-cluster">
            {"".join(f'<span class="carousel-dot-marker{" active" if i == current_idx else ""}"></span>' for i in range(total))}
        </div>
        """
        st.markdown(dots_html, unsafe_allow_html=True)

    with col_next:
        if st.button("→", key=f"feat_next_{current_idx}", use_container_width=True):
            st.session_state.featured_carousel_index = (current_idx + 1) % total
            st.session_state["_carousel_last_tick"] = time.time()
            st.rerun(scope="fragment")
