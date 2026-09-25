"""Single-Scheme Featured Government Schemes responsive auto-scrolling carousel component.

Displays exactly ONE scheme card at a time with real photographic banner image,
smooth transitions, previous/next navigation arrows, indicator dots, touch/mouse swipe,
auto-scroll every 4.5 seconds, and direct links to official government portals.
"""

import json
from typing import Any, Dict, List
import streamlit.components.v1 as components

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


def render_featured_carousel(schemes: List[Dict[str, Any]], lang: str = "en") -> None:
    """Renders a single-scheme carousel showing exactly ONE card at a time with navigation."""
    if not schemes:
        return

    items = []
    for s in schemes:
        slug = s.get("slug", "")
        category = s.get("category", "General")
        level = s.get("level", "Central")
        states = s.get("states", ["ALL"])
        state_label = ""
        if level != "Central" and states and "ALL" not in states:
            state_label = states[0]

        banner_url = get_scheme_banner_image(category, slug, s.get("image_url"))
        official_url = s.get("official_url", "")

        name = s.get("name_hi") if lang == "hi" and s.get("name_hi") else s.get("name", "")
        desc = s.get("description_hi") if lang == "hi" and s.get("description_hi") else s.get("description", "")
        if len(desc) > 140:
            desc = desc[:137] + "..."

        items.append({
            "name": name,
            "desc": desc,
            "category": category,
            "level": level,
            "state_label": state_label,
            "banner_url": banner_url,
            "official_url": official_url,
            "has_url": bool(official_url and official_url.startswith("http")),
        })

    view_btn_text = "योजना देखें →" if lang == "hi" else "View Scheme →"
    no_url_text = "आधिकारिक पोर्टल" if lang == "hi" else "Official Portal"
    central_badge = "केंद्रीय योजना" if lang == "hi" else "Central Scheme"
    state_badge = "राज्य योजना" if lang == "hi" else "State Scheme"

    items_json = json.dumps(items)

    html_code = f"""
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        * {{
          box-sizing: border-box;
          margin: 0;
          padding: 0;
        }}
        body {{
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
          background: transparent;
          color: #0F172A;
          user-select: none;
          -webkit-user-select: none;
          overflow: hidden;
        }}

        .single-carousel-wrapper {{
          position: relative;
          width: 100%;
          max-width: 100%;
          margin: 0 auto;
        }}

        .carousel-viewport {{
          overflow: hidden;
          width: 100%;
          border-radius: 14px;
          box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08);
          border: 1px solid #E2E8F0;
          background: #FFFFFF;
        }}

        .carousel-track {{
          display: flex;
          width: 100%;
          transition: transform 0.42s cubic-bezier(0.25, 1, 0.5, 1);
          will-change: transform;
        }}

        /* Exactly ONE card takes 100% of viewport */
        .scheme-card {{
          flex: 0 0 100%;
          width: 100%;
          background: #FFFFFF;
          display: flex;
          flex-direction: column;
          text-decoration: none;
          color: inherit;
          cursor: pointer;
        }}

        .card-banner {{
          width: 100%;
          height: 185px;
          overflow: hidden;
          background: #0F172A;
          position: relative;
        }}

        .card-banner img {{
          width: 100%;
          height: 100%;
          object-fit: cover;
          display: block;
          transition: transform 0.35s ease;
        }}

        .scheme-card:hover .card-banner img {{
          transform: scale(1.05);
        }}

        .card-body {{
          padding: 18px 20px 14px 20px;
          display: flex;
          flex-direction: column;
          flex: 1;
        }}

        .card-badges {{
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          margin-bottom: 10px;
        }}

        .badge {{
          font-size: 0.74rem;
          font-weight: 700;
          padding: 3px 9px;
          border-radius: 9999px;
          line-height: 1.2;
        }}

        .badge-cat {{
          background: #EFF6FF;
          color: #1D4ED8;
          border: 1px solid #DBEAFE;
        }}

        .badge-level {{
          background: #F8FAFC;
          color: #334155;
          border: 1px solid #E2E8F0;
        }}

        .card-title {{
          font-size: 1.15rem;
          font-weight: 800;
          color: #0F172A;
          line-height: 1.35;
          margin-bottom: 8px;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
          min-height: 2.7em;
        }}

        .card-desc {{
          font-size: 0.88rem;
          color: #64748B;
          line-height: 1.5;
          margin-bottom: 14px;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }}

        .card-footer {{
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding-top: 10px;
          border-top: 1px solid #F1F5F9;
        }}

        .btn-view {{
          display: inline-flex;
          align-items: center;
          gap: 4px;
          font-size: 0.86rem;
          font-weight: 700;
          color: #2563EB;
          padding: 6px 14px;
          background: #EFF6FF;
          border-radius: 6px;
          border: 1px solid #DBEAFE;
          transition: all 0.15s ease;
        }}

        .scheme-card:hover .btn-view {{
          background: #2563EB;
          color: #FFFFFF;
          border-color: #2563EB;
        }}

        /* Carousel Navigation Controls */
        .controls-row {{
          display: flex;
          align-items: center;
          gap: 12px;
        }}

        .nav-arrow {{
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: #F1F5F9;
          border: 1px solid #CBD5E1;
          color: #1E293B;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1rem;
          font-weight: bold;
          cursor: pointer;
          transition: all 0.15s ease;
        }}

        .nav-arrow:hover {{
          background: #1E293B;
          color: #FFFFFF;
          border-color: #1E293B;
          transform: scale(1.08);
        }}

        .dots-row {{
          display: flex;
          align-items: center;
          gap: 6px;
        }}

        .dot {{
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: #CBD5E1;
          cursor: pointer;
          transition: all 0.2s ease;
        }}

        .dot.active {{
          width: 20px;
          border-radius: 9999px;
          background: #2563EB;
        }}
      </style>
    </head>
    <body>
      <div class="single-carousel-wrapper" id="carouselWrapper">
        <div class="carousel-viewport" id="viewport">
          <div class="carousel-track" id="track"></div>
        </div>
      </div>

      <script>
        const schemes = {items_json};
        const viewBtnText = "{view_btn_text}";
        const noUrlText = "{no_url_text}";
        const centralBadge = "{central_badge}";
        const stateBadge = "{state_badge}";

        const track = document.getElementById("track");
        const viewport = document.getElementById("viewport");
        const wrapper = document.getElementById("carouselWrapper");

        let currentIndex = 0;
        let autoScrollTimer = null;
        let isHovered = false;
        const total = schemes.length;

        // Build single scheme cards
        schemes.forEach((s, idx) => {{
          const card = document.createElement("a");
          card.className = "scheme-card";
          if (s.has_url) {{
            card.href = s.official_url;
            card.target = "_blank";
            card.rel = "noopener noreferrer";
          }} else {{
            card.href = "javascript:void(0)";
          }}

          // 1. Photographic Banner Image
          const banner = document.createElement("div");
          banner.className = "card-banner";
          const img = document.createElement("img");
          img.src = s.banner_url;
          img.alt = s.name;
          img.loading = "lazy";
          img.onerror = function() {{
            this.src = "{FALLBACK_IMAGE}";
          }};
          banner.appendChild(img);
          card.appendChild(banner);

          // 2. Card Body
          const body = document.createElement("div");
          body.className = "card-body";

          // Badges
          const badges = document.createElement("div");
          badges.className = "card-badges";

          const badgeCat = document.createElement("span");
          badgeCat.className = "badge badge-cat";
          badgeCat.textContent = s.category;
          badges.appendChild(badgeCat);

          const badgeLevel = document.createElement("span");
          badgeLevel.className = "badge badge-level";
          badgeLevel.textContent = s.level === "Central" 
            ? centralBadge 
            : (s.state_label ? s.state_label : stateBadge);
          badges.appendChild(badgeLevel);

          body.appendChild(badges);

          // Title
          const title = document.createElement("div");
          title.className = "card-title";
          title.title = s.name;
          title.textContent = s.name;
          body.appendChild(title);

          // Description
          const desc = document.createElement("div");
          desc.className = "card-desc";
          desc.textContent = s.desc;
          body.appendChild(desc);

          // Footer with View button & Arrows / Dots
          const footer = document.createElement("div");
          footer.className = "card-footer";

          const btn = document.createElement("span");
          btn.className = s.has_url ? "btn-view" : "btn-disabled";
          btn.textContent = s.has_url ? viewBtnText : noUrlText;
          footer.appendChild(btn);

          // Controls row: [ ← ] [ ● ● ● ] [ → ]
          const controls = document.createElement("div");
          controls.className = "controls-row";

          const prevArrow = document.createElement("button");
          prevArrow.className = "nav-arrow";
          prevArrow.type = "button";
          prevArrow.setAttribute("aria-label", "Previous");
          prevArrow.textContent = "←";
          prevArrow.addEventListener("click", (e) => {{
            e.preventDefault();
            e.stopPropagation();
            prevSlide();
            resetAutoScroll();
          }});
          controls.appendChild(prevArrow);

          const dotsContainer = document.createElement("div");
          dotsContainer.className = "dots-row";
          dotsContainer.id = "dots-" + idx;
          controls.appendChild(dotsContainer);

          const nextArrow = document.createElement("button");
          nextArrow.className = "nav-arrow";
          nextArrow.type = "button";
          nextArrow.setAttribute("aria-label", "Next");
          nextArrow.textContent = "→";
          nextArrow.addEventListener("click", (e) => {{
            e.preventDefault();
            e.stopPropagation();
            nextSlide();
            resetAutoScroll();
          }});
          controls.appendChild(nextArrow);

          footer.appendChild(controls);
          body.appendChild(footer);
          card.appendChild(body);

          track.appendChild(card);
        }});

        function updateDots() {{
          for (let idx = 0; idx < total; idx++) {{
            const dotsEl = document.getElementById("dots-" + idx);
            if (!dotsEl) continue;
            dotsEl.innerHTML = "";
            for (let i = 0; i < total; i++) {{
              const dot = document.createElement("div");
              dot.className = "dot" + (i === currentIndex ? " active" : "");
              dot.addEventListener("click", (e) => {{
                e.preventDefault();
                e.stopPropagation();
                currentIndex = i;
                updatePosition();
                resetAutoScroll();
              }});
              dotsEl.appendChild(dot);
            }}
          }}
        }}

        function updatePosition() {{
          track.style.transform = `translateX(-${{currentIndex * 100}}%)`;
          updateDots();
        }}

        function nextSlide() {{
          currentIndex = (currentIndex + 1) % total;
          updatePosition();
        }}

        function prevSlide() {{
          currentIndex = (currentIndex - 1 + total) % total;
          updatePosition();
        }}

        function startAutoScroll() {{
          stopAutoScroll();
          autoScrollTimer = setInterval(() => {{
            if (!isHovered) {{
              nextSlide();
            }}
          }}, 4500);
        }}

        function stopAutoScroll() {{
          if (autoScrollTimer) {{
            clearInterval(autoScrollTimer);
            autoScrollTimer = null;
          }}
        }}

        function resetAutoScroll() {{
          stopAutoScroll();
          startAutoScroll();
        }}

        // Hover pause
        wrapper.addEventListener("mouseenter", () => {{
          isHovered = true;
        }});
        wrapper.addEventListener("mouseleave", () => {{
          isHovered = false;
        }});

        // Touch & Swipe Support
        let startX = 0;
        let isSwiping = false;

        viewport.addEventListener("touchstart", (e) => {{
          startX = e.touches[0].clientX;
          isSwiping = true;
          stopAutoScroll();
        }}, {{ passive: true }});

        viewport.addEventListener("touchend", (e) => {{
          if (!isSwiping) return;
          const endX = e.changedTouches[0].clientX;
          const diff = startX - endX;
          if (Math.abs(diff) > 40) {{
            if (diff > 0) nextSlide();
            else prevSlide();
          }}
          isSwiping = false;
          startAutoScroll();
        }}, {{ passive: true }});

        // Init
        updatePosition();
        startAutoScroll();
      </script>
    </body>
    </html>
    """

    components.html(html_code, height=450)
