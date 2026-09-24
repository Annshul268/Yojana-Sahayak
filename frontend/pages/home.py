"""Home page with Featured Schemes Carousel, Live Database Statistics, and 3-Step Guide."""

from typing import Any, Callable, Dict, List
import streamlit as st
from frontend.components.featured_carousel import render_featured_carousel
from frontend.services.api_client import api_client
from frontend.services.scheme_data import get_featured_schemes_db, get_live_db_statistics
from frontend.utils.i18n import get_current_language


def render_home(navigate_to: Callable[[str], None]) -> None:
    lang = get_current_language()

    # =========================================================================
    # 1. HERO SECTION (PREVIOUS SECTION)
    # =========================================================================
    st.markdown(
        f"""
        <div style="max-width: 880px; margin: 0 auto; text-align: center; padding: 20px 10px 6px 10px;">
            <div class="hero-tag-pill" style="display: inline-flex; margin-bottom: 16px;">
                <span>✓</span>
                <span>{"वे सरकारी योजनाएं खोजें जिनके लिए आप वास्तव में पात्र हैं" if lang == "hi" else "Find the government schemes you actually qualify for"}</span>
            </div>
            <h1 class="hero-headline" style="font-size: 2.85rem; margin-bottom: 16px; line-height: 1.18;">
                {"सरकारी लाभ, सरल भाषा में समझें" if lang == "hi" else "Government benefits, explained in plain language"}
            </h1>
            <p class="hero-subhead" style="font-size: 1.12rem; max-width: 760px; margin: 0 auto 24px auto;">
                {"अपने बारे में कुछ सरल प्रश्नों के उत्तर दें। हम आधिकारिक केंद्रीय एवं राज्य योजनाओं के साथ आपके विवरण का मिलान करते हैं और बताते हैं कि आप क्यों पात्र हैं, कौन से दस्तावेज चाहिए, और आवेदन कैसे करें।" if lang == "hi" else "Answer a few simple questions about yourself. We match you against official central and state schemes and tell you why you qualify, which documents you need, and exactly how to apply."}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Action buttons centered
    col_b_spacer1, col_b1, col_b2, col_b_spacer2 = st.columns([1.5, 2, 2, 1.5])
    with col_b1:
        if st.button(
            "पात्रता जांचें →" if lang == "hi" else "Check my eligibility →",
            type="primary",
            use_container_width=True,
            key="hero_check_eligibility_btn",
        ):
            navigate_to("finder")

    with col_b2:
        if st.button(
            "सभी योजनाएं" if lang == "hi" else "Browse all schemes",
            type="secondary",
            use_container_width=True,
            key="hero_browse_schemes_btn",
        ):
            navigate_to("schemes")

    st.markdown(
        f"""
        <div class="hero-footnote" style="text-align: center; margin-top: 14px; margin-bottom: 6px;">
            {"प्रत्येक परिणाम आधिकारिक सरकारी स्रोत से जुड़ा है। हम कभी कोई योजना नहीं बनाते।" if lang == "hi" else "Every result links to an official government source. We never invent a scheme."}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 32px 0 26px 0;' />", unsafe_allow_html=True)

    # =========================================================================
    # 2. FEATURED GOVERNMENT SCHEMES CAROUSEL
    # Replaces the Categories Covered block
    # =========================================================================
    st.markdown(
        f"""
        <div class="discovery-section-header" style="text-align: center; margin-bottom: 6px;">
            <h2 class="discovery-title" style="font-size: 2rem; font-weight: 800; color: #0F172A; margin-bottom: 4px; letter-spacing: -0.3px;">
                {"प्रमुख सरकारी योजनाएं" if lang == "hi" else "FEATURED GOVERNMENT SCHEMES"}
            </h2>
            <p class="discovery-subtitle" style="font-size: 1rem; color: #475569; margin: 0;">
                {"भारत भर में उपलब्ध महत्वपूर्ण सरकारी योजनाओं का अन्वेषण करें" if lang == "hi" else "Explore important government schemes available across India"}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Resilient featured schemes retrieval with verified images
    featured_schemes = get_featured_schemes_db(limit=5)
    if not featured_schemes:
        featured_res = api_client.get_featured_schemes(limit=5)
        featured_schemes = featured_res.get("data", []) if featured_res.get("ok") else []

    if featured_schemes:
        render_featured_carousel(featured_schemes, lang=lang)
    else:
        st.info("Featured schemes are currently loading...")

    st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 36px 0 28px 0;' />", unsafe_allow_html=True)

    # =========================================================================
    # 3. CATEGORY SCHEME COUNTS (10 Verified Categories with Live DB Counts)
    # =========================================================================
    stats = get_live_db_statistics()
    category_counts = stats.get("categories", {})

    st.markdown(
        f"""
        <div style="margin-top: 10px; margin-bottom: 18px;">
            <h3 style="font-size: 1.35rem; font-weight: 800; color: #0F172A; margin-bottom: 4px;">
                {"श्रेणी अनुसार योजनाएं" if lang == "hi" else "Scheme Counts by Category"}
            </h3>
            <p style="font-size: 0.92rem; color: #64748B; margin: 0;">
                {"प्रत्येक प्रमुख श्रेणी के लिए उपलब्ध योजनाओं की वास्तविक संख्या (डेटाबेस से सीधे सत्यापित)" if lang == "hi" else "Real-time scheme counts for every primary sector, directly queried from the database"}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ordered_categories = [
        ("Education & Scholarships", "Education & Learning", "🎓", "शिक्षा एवं छात्रवृत्ति"),
        ("Health", "Healthcare", "🏥", "स्वास्थ्य"),
        ("Housing", "Housing & Shelter", "🏠", "आवास"),
        ("Agriculture", "Agriculture & Rural Development", "🌾", "कृषि"),
        ("Business & Loans", "Business & Self Employment", "📈", "व्यवसाय एवं ऋण"),
        ("Employment & Skills", "Employment & Skills", "💼", "रोजगार एवं कौशल"),
        ("Pension", "Social Security & Pension", "👴", "पेंशन"),
        ("Insurance", "Financial Assistance", "💳", "बीमा / वित्तीय"),
        ("Women & Child", "Women & Child Development", "👩‍👧", "महिला एवं बाल विकास"),
        ("Disability Support", "Differently Abled Support", "♿", "दिव्यांगजन सहायता"),
    ]

    col_cat_l, col_cat_r = st.columns(2, gap="medium")
    half_cat = len(ordered_categories) // 2

    for idx, (display_name, db_cat_name, icon, hindi_name) in enumerate(ordered_categories):
        count_val = category_counts.get(display_name, 0)
        target_column = col_cat_l if idx < half_cat else col_cat_r
        disp_title = hindi_name if lang == "hi" else display_name

        with target_column:
            c_info, c_btn = st.columns([7, 3])
            with c_info:
                st.markdown(
                    f"""
                    <div class="category-stat-bar">
                        <span class="cat-stat-name">{icon} {disp_title}</span>
                        <span class="cat-stat-count">{count_val}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_btn:
                btn_cat_label = f"देखें ({count_val})" if lang == "hi" else f"View ({count_val})"
                if st.button(btn_cat_label, key=f"btn_cat_direct_{idx}", use_container_width=True):
                    st.session_state.selected_category_filter = db_cat_name
                    navigate_to("schemes")

    st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 40px 0 28px 0;' />", unsafe_allow_html=True)

    # =========================================================================
    # 5. HOW YOJANA SAHAYAK WORKS (3-STEP GUIDED PROCESS)
    # =========================================================================
    col_s1, col_s2, col_s3 = st.columns(3, gap="medium")

    with col_s1:
        st.markdown(
            f"""
            <div class="step-card">
                <div class="step-icon-box">📋</div>
                <div class="step-label">{"चरण 1" if lang == "hi" else "Step 1"}</div>
                <div class="step-title">{"अपने बारे में बताएं" if lang == "hi" else "Tell us about yourself"}</div>
                <div class="step-desc">
                    {"एक मार्गदर्शित प्रपत्र: राज्य, आयु, कार्य, आय, सामाजिक श्रेणी और आवश्यक सहायता।" if lang == "hi" else "A guided form: state, age, work, income, category and what you need help with."}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_s2:
        st.markdown(
            f"""
            <div class="step-card">
                <div class="step-icon-box">🔍</div>
                <div class="step-label">{"चरण 2" if lang == "hi" else "Step 2"}</div>
                <div class="step-title">{"हम आधिकारिक नियमों से मिलाते हैं" if lang == "hi" else "We match official rules"}</div>
                <div class="step-desc">
                    {"हम प्रत्येक योजना के नियमों के अनुसार जांचते हैं। कोई अनुमान नहीं। केवल वास्तविक पात्रता।" if lang == "hi" else "We check every scheme against its official eligibility rules. No guessing. Only real eligibility."}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_s3:
        st.markdown(
            f"""
            <div class="step-card">
                <div class="step-icon-box">🎯</div>
                <div class="step-label">{"चरण 3" if lang == "hi" else "Step 3"}</div>
                <div class="step-title">{"चरण-दर-चरण मार्गदर्शन" if lang == "hi" else "Step-by-step guidance"}</div>
                <div class="step-desc">
                    {"जानिए आपको क्या मिलेगा, कौन से दस्तावेज चाहिए, और सीधे आधिकारिक पोर्टल पर आवेदन कैसे करें।" if lang == "hi" else "See what you get, what documents you need, and how to apply directly on official portals."}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
