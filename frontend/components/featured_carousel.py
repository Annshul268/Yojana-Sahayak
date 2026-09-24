"""Featured Government Schemes auto-scrolling responsive carousel component."""

import json
from typing import Any, Dict, List
import streamlit.components.v1 as components


def get_scheme_banner_svg(category: str, slug: str) -> str:
    """Returns an inline SVG data URI representing a crisp, modern banner for the scheme."""
    c_lower = (category or "").lower()
    s_lower = (slug or "").lower()

    if "scholarship" in s_lower or "education" in c_lower:
        # Education / Scholarship banner (Navy & Gold)
        return """data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="150" viewBox="0 0 400 150">
          <defs>
            <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="%231E3A8A" />
              <stop offset="100%" stop-color="%232563EB" />
            </linearGradient>
          </defs>
          <rect width="400" height="150" fill="url(%23g1)"/>
          <circle cx="340" cy="75" r="70" fill="%23FFFFFF" opacity="0.08"/>
          <circle cx="70" cy="130" r="50" fill="%23F59E0B" opacity="0.15"/>
          <g transform="translate(170, 40) scale(1.4)" fill="%23FBBF24">
            <path d="M12 3L1 9l11 6 9-4.91V17h2V9L12 3z"/>
            <path d="M5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z" fill="%23FFFFFF" opacity="0.9"/>
          </g>
          <text x="20" y="125" fill="%23FFFFFF" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="700" font-size="14" letter-spacing="1">EDUCATION &amp; SCHOLARSHIP</text>
        </svg>"""
    elif "awas" in s_lower or "pmay" in s_lower or "housing" in c_lower:
        # Housing banner (Teal & Emerald)
        return """data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="150" viewBox="0 0 400 150">
          <defs>
            <linearGradient id="g2" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="%23065F46" />
              <stop offset="100%" stop-color="%23059669" />
            </linearGradient>
          </defs>
          <rect width="400" height="150" fill="url(%23g2)"/>
          <circle cx="330" cy="40" r="60" fill="%2334D399" opacity="0.15"/>
          <g transform="translate(175, 45) scale(1.4)" fill="%23FFFFFF">
            <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
          </g>
          <text x="20" y="125" fill="%23FFFFFF" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="700" font-size="14" letter-spacing="1">HOUSING FOR ALL</text>
        </svg>"""
    elif "adip" in s_lower or "disab" in c_lower or "divyang" in s_lower:
        # Disability support banner (Indigo & Violet)
        return """data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="150" viewBox="0 0 400 150">
          <defs>
            <linearGradient id="g3" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="%234338CA" />
              <stop offset="100%" stop-color="%236366F1" />
            </linearGradient>
          </defs>
          <rect width="400" height="150" fill="url(%23g3)"/>
          <circle cx="340" cy="90" r="60" fill="%23A5B4FC" opacity="0.2"/>
          <g transform="translate(180, 42) scale(1.4)" fill="%23FFFFFF">
            <circle cx="12" cy="4" r="2"/>
            <path d="M19 13v-2c-1.54.02-3.09-.75-4.07-1.83l-1.29-1.43c-.17-.19-.38-.34-.61-.45-.01 0-.01-.01-.02-.01H13c-.35-.2-.75-.3-1.19-.26C10.76 7.11 10 8.04 10 9.09V15c0 1.1.9 2 2 2h5v5h2v-7h-4v-4.14c.54.34 1.15.54 1.79.54h2.21zM6.5 15.5c0 .83.67 1.5 1.5 1.5.54 0 1.01-.28 1.28-.71l1.55.9C10.3 18.23 9.24 19 8 19c-1.93 0-3.5-1.57-3.5-3.5S6.07 12 8 12c.79 0 1.53.27 2.12.72l-1.39 1.05C8.42 13.62 8.22 13.5 8 13.5c-.83 0-1.5.67-1.5 2z"/>
          </g>
          <text x="20" y="125" fill="%23FFFFFF" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="700" font-size="14" letter-spacing="1">DIVYANGJAN SUPPORT</text>
        </svg>"""
    elif "ayushman" in s_lower or "health" in c_lower:
        # Healthcare banner (Crimson & Rose)
        return """data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="150" viewBox="0 0 400 150">
          <defs>
            <linearGradient id="g4" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="%23991B1B" />
              <stop offset="100%" stop-color="%23DC2626" />
            </linearGradient>
          </defs>
          <rect width="400" height="150" fill="url(%23g4)"/>
          <circle cx="330" cy="50" r="65" fill="%23FCA5A5" opacity="0.15"/>
          <g transform="translate(180, 45) scale(1.4)" fill="%23FFFFFF">
            <path d="M19 10.5h-4.5V6h-5v4.5H5v5h4.5V20h5v-4.5H19z"/>
          </g>
          <text x="20" y="125" fill="%23FFFFFF" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="700" font-size="14" letter-spacing="1">HEALTHCARE &amp; PROTECTION</text>
        </svg>"""
    elif "kisan" in s_lower or "farm" in c_lower or "agri" in c_lower:
        # Agriculture / Farmer banner (Amber & Forest Green)
        return """data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="150" viewBox="0 0 400 150">
          <defs>
            <linearGradient id="g5" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="%2314532D" />
              <stop offset="100%" stop-color="%2316A34A" />
            </linearGradient>
          </defs>
          <rect width="400" height="150" fill="url(%23g5)"/>
          <circle cx="340" cy="80" r="65" fill="%23FDE047" opacity="0.15"/>
          <g transform="translate(178, 42) scale(1.4)" fill="%23FDE047">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" opacity="0.25"/>
            <path d="M7 17l5-5 5 5-1.41 1.41L12 14.83l-3.59 3.58z" fill="%23FFFFFF"/>
          </g>
          <text x="20" y="125" fill="%23FFFFFF" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="700" font-size="14" letter-spacing="1">AGRICULTURE &amp; FARMERS</text>
        </svg>"""
    else:
        # Default Civic Emblem Banner (Slate & Blue)
        return """data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="150" viewBox="0 0 400 150">
          <defs>
            <linearGradient id="g0" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="%231E293B" />
              <stop offset="100%" stop-color="%23334155" />
            </linearGradient>
          </defs>
          <rect width="400" height="150" fill="url(%23g0)"/>
          <circle cx="340" cy="75" r="70" fill="%23FFFFFF" opacity="0.06"/>
          <g transform="translate(180, 45) scale(1.4)" fill="%2394A3B8">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
          </g>
          <text x="20" y="125" fill="%23FFFFFF" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-weight="700" font-size="14" letter-spacing="1">GOVERNMENT WELFARE SCHEME</text>
        </svg>"""


def render_featured_carousel(schemes: List[Dict[str, Any]], lang: str = "en") -> None:
    """Renders a self-contained HTML/CSS/JavaScript auto-scrolling scheme carousel."""
    if not schemes:
        return

    # Process items with banners and safe texts
    items = []
    for s in schemes:
        slug = s.get("slug", "")
        category = s.get("category", "General")
        level = s.get("level", "Central")
        states = s.get("states", ["ALL"])
        state_label = ""
        if level != "Central" and states and "ALL" not in states:
            state_label = states[0]

        banner_url = s.get("image_url") or get_scheme_banner_svg(category, slug)
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
    no_url_text = "आधिकारिक लिंक अनुपलब्ध" if lang == "hi" else "Official link unavailable"
    central_badge = "केंद्रीय सरकार" if lang == "hi" else "Central Scheme"
    state_badge = "राज्य सरकार" if lang == "hi" else "State Scheme"

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

        .carousel-wrapper {{
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
        }}

        .scheme-card:hover {{
          transform: translateY(-3px);
          box-shadow: 0 10px 22px rgba(15, 23, 42, 0.1);
          border-color: #CBD5E1;
        }}

        .card-banner {{
          width: 100%;
          height: 128px;
          background-size: cover;
          background-position: center;
          background-repeat: no-repeat;
          border-bottom: 1px solid #F1F5F9;
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
          font-weight: 600;
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
          font-size: 1.02rem;
          font-weight: 700;
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
          font-size: 0.84rem;
          color: #64748B;
          line-height: 1.45;
          margin-bottom: 16px;
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
          justify-content: space-between;
          padding-top: 10px;
          border-top: 1px solid #F1F5F9;
        }}

        .btn-view {{
          display: inline-flex;
          align-items: center;
          gap: 4px;
          font-size: 0.86rem;
          font-weight: 600;
          color: #2563EB;
          text-decoration: none;
          cursor: pointer;
          transition: color 0.15s ease;
        }}

        .btn-view:hover {{
          color: #1D4ED8;
          text-decoration: underline;
        }}

        .btn-disabled {{
          color: #94A3B8;
          font-size: 0.8rem;
          font-style: italic;
        }}

        /* Navigation Arrows */
        .nav-btn {{
          position: absolute;
          top: 50%;
          transform: translateY(-50%);
          width: 38px;
          height: 38px;
          border-radius: 50%;
          background: #FFFFFF;
          border: 1px solid #CBD5E1;
          color: #1E293B;
          box-shadow: 0 4px 10px rgba(0,0,0,0.08);
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          font-size: 1.15rem;
          font-weight: bold;
          z-index: 10;
          transition: background 0.15s, box-shadow 0.15s, transform 0.15s;
        }}

        .nav-btn:hover {{
          background: #F8FAFC;
          box-shadow: 0 6px 14px rgba(0,0,0,0.12);
          transform: translateY(-50%) scale(1.05);
        }}

        .nav-prev {{
          left: 4px;
        }}

        .nav-next {{
          right: 4px;
        }}

        /* Pagination Indicators */
        .dots-container {{
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 6px;
          margin-top: 14px;
        }}

        .dot {{
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #CBD5E1;
          cursor: pointer;
          transition: background 0.2s, transform 0.2s;
        }}

        .dot.active {{
          background: #2563EB;
          width: 20px;
          border-radius: 4px;
        }}

        /* Responsive Breakpoints */
        @media (max-width: 899px) and (min-width: 600px) {{
          .scheme-card {{
            flex: 0 0 calc((100% - 18px) / 2); /* Tablet: 2 cards */
          }}
        }}

        @media (max-width: 599px) {{
          .carousel-wrapper {{
            padding: 10px 36px;
          }}
          .scheme-card {{
            flex: 0 0 100%; /* Mobile: 1 card */
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
      <div class="carousel-wrapper" id="carouselWrapper">
        <button class="nav-btn nav-prev" id="prevBtn" aria-label="Previous schemes">‹</button>
        <button class="nav-btn nav-next" id="nextBtn" aria-label="Next schemes">›</button>

        <div class="carousel-viewport" id="viewport">
          <div class="carousel-track" id="track"></div>
        </div>

        <div class="dots-container" id="dots"></div>
      </div>

      <script>
        const schemes = {items_json};
        const viewBtnText = "{view_btn_text}";
        const noUrlText = "{no_url_text}";
        const centralBadge = "{central_badge}";
        const stateBadge = "{state_badge}";

        const track = document.getElementById("track");
        const dotsContainer = document.getElementById("dots");
        const prevBtn = document.getElementById("prevBtn");
        const nextBtn = document.getElementById("nextBtn");
        const wrapper = document.getElementById("carouselWrapper");

        let currentIndex = 0;
        let autoScrollTimer = null;
        let isHovered = false;

        // Populate cards
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

          const levelLabel = s.level === "Central" 
            ? centralBadge 
            : (s.state_label ? s.state_label : stateBadge);

          card.innerHTML = `
            <div class="card-banner" style="background-image: url('${{s.banner_url}}');"></div>
            <div class="card-body">
              <div class="card-badges">
                <span class="badge badge-cat">${{s.category}}</span>
                <span class="badge badge-level">${{levelLabel}}</span>
              </div>
              <div class="card-title" title="${{s.name}}">${{s.name}}</div>
              <div class="card-desc">${{s.desc}}</div>
              <div class="card-action">
                ${{s.has_url 
                  ? `<span class="btn-view">${{viewBtnText}}</span>` 
                  : `<span class="btn-disabled">${{noUrlText}}</span>`
                }}
              </div>
            </div>
          `;
          track.appendChild(card);
        }});

        function getVisibleCount() {{
          const width = window.innerWidth;
          if (width < 600) return 1;
          if (width < 900) return 2;
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
              updateCarousel();
              resetTimer();
            }});
            dotsContainer.appendChild(dot);
          }}
        }}

        function updateCarousel() {{
          const maxIdx = getMaxIndex();
          if (currentIndex > maxIdx) currentIndex = 0;
          if (currentIndex < 0) currentIndex = maxIdx;

          const visible = getVisibleCount();
          const cardWidthPercent = 100 / visible;
          // Approximate shift based on card fraction + gap
          const firstCard = track.children[0];
          if (firstCard) {{
            const cardWidth = firstCard.getBoundingClientRect().width;
            const gap = 18;
            const offset = currentIndex * (cardWidth + gap);
            track.style.transform = `translateX(-${{offset}}px)`;
          }}

          // Update active dot
          const dots = dotsContainer.children;
          for (let i = 0; i < dots.length; i++) {{
            dots[i].className = "dot" + (i === currentIndex ? " active" : "");
          }}
        }}

        function nextSlide() {{
          const maxIdx = getMaxIndex();
          if (currentIndex >= maxIdx) {{
            currentIndex = 0;
          }} else {{
            currentIndex++;
          }}
          updateCarousel();
        }}

        function prevSlide() {{
          const maxIdx = getMaxIndex();
          if (currentIndex <= 0) {{
            currentIndex = maxIdx;
          }} else {{
            currentIndex--;
          }}
          updateCarousel();
        }}

        function resetTimer() {{
          clearInterval(autoScrollTimer);
          if (!isHovered) {{
            autoScrollTimer = setInterval(nextSlide, 4500);
          }}
        }}

        // Controls
        nextBtn.addEventListener("click", (e) => {{
          e.stopPropagation();
          nextSlide();
          resetTimer();
        }});

        prevBtn.addEventListener("click", (e) => {{
          e.stopPropagation();
          prevSlide();
          resetTimer();
        }});

        // Hover pause
        wrapper.addEventListener("mouseenter", () => {{
          isHovered = true;
          clearInterval(autoScrollTimer);
        }});

        wrapper.addEventListener("mouseleave", () => {{
          isHovered = false;
          resetTimer();
        }});

        // Touch & Swipe Support
        let startX = 0;
        let isSwiping = false;

        wrapper.addEventListener("touchstart", (e) => {{
          isHovered = true;
          clearInterval(autoScrollTimer);
          startX = e.touches[0].clientX;
          isSwiping = true;
        }}, {{ passive: true }});

        wrapper.addEventListener("touchend", (e) => {{
          if (!isSwiping) return;
          const endX = e.changedTouches[0].clientX;
          const diff = startX - endX;
          if (Math.abs(diff) > 40) {{
            if (diff > 0) {{
              nextSlide();
            }} else {{
              prevSlide();
            }}
          }}
          isSwiping = false;
          isHovered = false;
          resetTimer();
        }}, {{ passive: true }});

        window.addEventListener("resize", () => {{
          updateDots();
          updateCarousel();
        }});

        // Initial setup
        updateDots();
        updateCarousel();
        resetTimer();
      </script>
    </body>
    </html>
    """

    components.html(html_code, height=440, scrolling=False)
