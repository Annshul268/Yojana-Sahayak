"""Featured Government Schemes auto-scrolling responsive carousel component.

Provides clean, real-image scheme cards with touch/mouse swipe, left/right arrows,
auto-scroll, responsive 3/2/1 card layouts, and direct official scheme URLs.
"""

import json
from typing import Any, Dict, List
import streamlit.components.v1 as components

# High-resolution, real photographic images for government sectors
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
    """Renders a self-contained HTML/CSS/JavaScript auto-scrolling scheme carousel."""
    if not schemes:
        return

    # Process items with real banner images and sanitized texts
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
        if len(desc) > 130:
            desc = desc[:127] + "..."

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

        .carousel-container {{
          position: relative;
          width: 100%;
          max-width: 1180px;
          margin: 0 auto;
          padding: 10px 48px;
        }}

        .carousel-viewport {{
          overflow: hidden;
          width: 100%;
          border-radius: 14px;
        }}

        .carousel-track {{
          display: flex;
          transition: transform 0.45s cubic-bezier(0.25, 1, 0.5, 1);
          gap: 18px;
          will-change: transform;
        }}

        /* Card element */
        .scheme-card {{
          flex: 0 0 calc((100% - 36px) / 3); /* Desktop: 3 cards */
          background: #FFFFFF;
          border: 1px solid #E2E8F0;
          border-radius: 12px;
          overflow: hidden;
          display: flex;
          flex-direction: column;
          box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
          transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
          text-decoration: none;
          color: inherit;
          cursor: pointer;
        }}

        .scheme-card:hover {{
          transform: translateY(-4px);
          box-shadow: 0 12px 24px rgba(15, 23, 42, 0.12);
          border-color: #CBD5E1;
        }}

        .card-banner {{
          width: 100%;
          height: 135px;
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
          transform: scale(1.06);
        }}

        .card-body {{
          padding: 16px;
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
          font-size: 0.72rem;
          font-weight: 700;
          padding: 3px 8px;
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
          font-size: 0.98rem;
          font-weight: 800;
          color: #0F172A;
          line-height: 1.35;
          margin-bottom: 8px;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
          min-height: 2.65em;
        }}

        .card-desc {{
          font-size: 0.83rem;
          color: #64748B;
          line-height: 1.45;
          margin-bottom: 14px;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
          flex: 1;
        }}

        .card-action {{
          margin-top: auto;
          display: flex;
          align-items: center;
          justify-content: flex-end;
          padding-top: 10px;
          border-top: 1px solid #F1F5F9;
        }}

        .btn-view {{
          display: inline-flex;
          align-items: center;
          gap: 4px;
          font-size: 0.82rem;
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

        .btn-disabled {{
          font-size: 0.82rem;
          font-weight: 600;
          color: #94A3B8;
        }}

        /* Navigation Arrows */
        .nav-btn {{
          position: absolute;
          top: calc(50% - 15px);
          width: 38px;
          height: 38px;
          border-radius: 50%;
          background: #FFFFFF;
          border: 1px solid #CBD5E1;
          color: #1E293B;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.2rem;
          font-weight: bold;
          cursor: pointer;
          box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
          transition: all 0.15s ease;
          z-index: 10;
        }}

        .nav-btn:hover {{
          background: #1E293B;
          color: #FFFFFF;
          border-color: #1E293B;
          transform: scale(1.08);
        }}

        .nav-btn.prev {{ left: 2px; }}
        .nav-btn.next {{ right: 2px; }}

        /* Indicator Dots */
        .dots-container {{
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 7px;
          margin-top: 14px;
        }}

        .dot {{
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #CBD5E1;
          cursor: pointer;
          transition: all 0.2s ease;
        }}

        .dot.active {{
          width: 24px;
          border-radius: 9999px;
          background: #2563EB;
        }}

        /* Responsive breakpoints: 3 on desktop, 2 on tablet, 1 on mobile */
        @media (max-width: 900px) {{
          .scheme-card {{
            flex: 0 0 calc((100% - 18px) / 2); /* Tablet: 2 cards */
          }}
          .carousel-container {{
            padding: 10px 42px;
          }}
        }}

        @media (max-width: 600px) {{
          .scheme-card {{
            flex: 0 0 100%; /* Mobile: 1 card */
          }}
          .carousel-container {{
            padding: 10px 36px;
          }}
          .nav-btn {{
            width: 32px;
            height: 32px;
            font-size: 1rem;
          }}
        }}
      </style>
    </head>
    <body>
      <div class="carousel-container" id="carouselWrapper">
        <button class="nav-btn prev" id="prevBtn" aria-label="Previous scheme">‹</button>
        <div class="carousel-viewport" id="viewport">
          <div class="carousel-track" id="track"></div>
        </div>
        <button class="nav-btn next" id="nextBtn" aria-label="Next scheme">›</button>
        <div class="dots-container" id="dots"></div>
      </div>

      <script>
        const schemes = {items_json};
        const viewBtnText = "{view_btn_text}";
        const noUrlText = "{no_url_text}";
        const centralBadge = "{central_badge}";
        const stateBadge = "{state_badge}";

        const track = document.getElementById("track");
        const prevBtn = document.getElementById("prevBtn");
        const nextBtn = document.getElementById("nextBtn");
        const dotsContainer = document.getElementById("dots");
        const viewport = document.getElementById("viewport");
        const wrapper = document.getElementById("carouselWrapper");

        let currentIndex = 0;
        let autoScrollTimer = null;
        let isHovered = false;

        // Populate cards using safe DOM methods (eliminates any string escaping or syntax bugs)
        schemes.forEach((s) => {{
          const card = document.createElement("a");
          card.className = "scheme-card";
          if (s.has_url) {{
            card.href = s.official_url;
            card.target = "_blank";
            card.rel = "noopener noreferrer";
          }} else {{
            card.href = "javascript:void(0)";
          }}

          // 1. Banner with Real Image
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

          // Action Button
          const action = document.createElement("div");
          action.className = "card-action";

          const btn = document.createElement("span");
          btn.className = s.has_url ? "btn-view" : "btn-disabled";
          btn.textContent = s.has_url ? viewBtnText : noUrlText;
          action.appendChild(btn);

          body.appendChild(action);
          card.appendChild(body);

          track.appendChild(card);
        }});

        function getVisibleCount() {{
          const width = window.innerWidth;
          if (width <= 600) return 1;
          if (width <= 900) return 2;
          return 3;
        }}

        function getMaxIndex() {{
          const visible = getVisibleCount();
          return Math.max(0, schemes.length - visible);
        }}

        function updateDots() {{
          dotsContainer.innerHTML = "";
          const maxIdx = getMaxIndex();
          for (let i = 0; i <= maxIdx; i++) {{
            const dot = document.createElement("div");
            dot.className = "dot" + (i === currentIndex ? " active" : "");
            dot.addEventListener("click", () => {{
              currentIndex = i;
              updatePosition();
              resetAutoScroll();
            }});
            dotsContainer.appendChild(dot);
          }}
        }}

        function updatePosition() {{
          const maxIdx = getMaxIndex();
          if (currentIndex > maxIdx) currentIndex = maxIdx;
          if (currentIndex < 0) currentIndex = 0;

          const cards = track.children;
          if (cards.length > 0) {{
            const cardWidth = cards[0].offsetWidth;
            const gap = 18;
            const offset = currentIndex * (cardWidth + gap);
            track.style.transform = `translateX(-${{offset}}px)`;
          }}
          updateDots();
        }}

        function nextSlide() {{
          const maxIdx = getMaxIndex();
          if (currentIndex >= maxIdx) {{
            currentIndex = 0;
          }} else {{
            currentIndex++;
          }}
          updatePosition();
        }}

        function prevSlide() {{
          const maxIdx = getMaxIndex();
          if (currentIndex <= 0) {{
            currentIndex = maxIdx;
          }} else {{
            currentIndex--;
          }}
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

        // Controls
        nextBtn.addEventListener("click", () => {{
          nextSlide();
          resetAutoScroll();
        }});

        prevBtn.addEventListener("click", () => {{
          prevSlide();
          resetAutoScroll();
        }});

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

        // Resize handler
        window.addEventListener("resize", () => {{
          updatePosition();
        }});

        // Init
        updatePosition();
        startAutoScroll();
      </script>
    </body>
    </html>
    """

    components.html(html_code, height=430)
