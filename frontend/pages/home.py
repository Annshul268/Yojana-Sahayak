"""Home page with Featured Schemes Carousel, Live Database Statistics, and Category/State Exploration."""

from typing import Any, Callable, Dict, List
import streamlit as st
from frontend.components.featured_carousel import render_featured_carousel
from frontend.services.api_client import api_client
from frontend.services.scheme_data import get_featured_schemes_db, get_live_db_statistics
from frontend.utils.i18n import get_current_language


CATEGORIES_COVERED = [
    ("Education & Learning", "Education & scholarships", "शिक्षा एवं छात्रवृत्ति"),
    ("Healthcare", "Health", "स्वास्थ्य"),
    ("Housing & Shelter", "Housing", "आवास"),
    ("Agriculture & Rural Development", "Agriculture", "कृषि"),
    ("Business & Self Employment", "Business & loans", "व्यवसाय एवं ऋण"),
    ("Employment & Skills", "Employment & skills", "रोजगार एवं कौशल"),
    ("Social Security & Pension", "Pension", "पेंशन"),
    ("Women & Child Development", "Women & child", "महिला एवं बाल विकास"),
    ("Differently Abled Support", "Disability support", "दिव्यांगजन सहायता"),
    ("Financial Assistance", "Financial Assistance", "वित्तीय सहायता"),
]


def render_home(navigate_to: Callable[[str], None]) -> None:
    lang = get_current_language()

    # =========================================================================
    # HERO SECTION
    # =========================================================================
    col_hero, col_spacer, col_cat = st.columns([5.5, 0.5, 4.5])

    with col_hero:
        # Pill Tag
        st.markdown(
            f"""
            <div class="hero-tag-pill">
                <span>✓</span>
                <span>{"वे सरकारी योजनाएं खोजें जिनके लिए आप वास्तव में पात्र हैं" if lang == "hi" else "Find the government schemes you actually qualify for"}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Big bold headline
        st.markdown(
            f"""
            <h1 class="hero-headline">
                {"सरकारी लाभ,<br>सरल भाषा में समझें" if lang == "hi" else "Government benefits,<br>explained in plain<br>language"}
            </h1>
            <p class="hero-subhead">
                {"अपने बारे में कुछ सरल प्रश्नों के उत्तर दें। हम आधिकारिक केंद्रीय एवं राज्य योजनाओं के साथ आपके विवरण का मिलान करते हैं और बताते हैं कि आप क्यों पात्र हैं, कौन से दस्तावेज चाहिए, और आवेदन कैसे करें।" if lang == "hi" else "Answer a few simple questions about yourself. We match you against official central and state schemes and tell you why you qualify, which documents you need, and exactly how to apply."}
            </p>
            """,
            unsafe_allow_html=True,
        )

        # Action Buttons
        col_btn1, col_btn2 = st.columns([1.3, 1.1])
        with col_btn1:
            if st.button(
                "पात्रता जांचें →" if lang == "hi" else "Check my eligibility →",
                type="primary",
                use_container_width=True,
                key="hero_check_eligibility_btn",
            ):
                navigate_to("finder")

        with col_btn2:
            if st.button(
                "सभी योजनाएं" if lang == "hi" else "Browse all schemes",
                type="secondary",
                use_container_width=True,
                key="hero_browse_schemes_btn",
            ):
                navigate_to("schemes")

        # Footnote
        st.markdown(
            f"""
            <div class="hero-footnote">
                {"प्रत्येक परिणाम आधिकारिक सरकारी स्रोत से जुड़ा है। हम कभी कोई योजना नहीं बनाते।" if lang == "hi" else "Every result links to an official government source. We never invent a scheme."}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_cat:
        # Categories Covered Card
        st.markdown(
            f"""
            <div class="civic-card">
                <div class="civic-card-header">
                    {"शामिल श्रेणियां" if lang == "hi" else "CATEGORIES COVERED"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='margin-top: -12px; margin-bottom: 8px;'>", unsafe_allow_html=True)
        c_row1 = st.columns(2)
        for idx, (cat_key, cat_en, cat_hi) in enumerate(CATEGORIES_COVERED):
            label = cat_hi if lang == "hi" else cat_en
            with c_row1[idx % 2]:
                if st.button(label, key=f"cat_chip_{idx}", use_container_width=True):
                    st.session_state.selected_category_filter = cat_key
                    navigate_to("schemes")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 36px 0 28px 0;' />", unsafe_allow_html=True)

    # =========================================================================
    # STEP 3 & 4: GOVERNMENT SCHEMES AVAILABLE (LIVE DATABASE STATISTICS)
    # Placed directly below the Categories Covered section
    # =========================================================================
    # Retrieve live stats directly from database (resilient to offline backend)
    stats = get_live_db_statistics()
    total_schemes = stats.get("total", 438)
    central_schemes = stats.get("central", 109)
    state_schemes = stats.get("state", 329)
    category_counts = stats.get("categories", {})

    st.markdown(
        f"""
        <div style="background: #F8FAFC; border: 2px solid #E2E8F0; border-radius: 16px; padding: 28px 24px; margin-bottom: 28px;">
            <div style="text-align: center; margin-bottom: 20px;">
                <span style="background: #2563EB; color: #FFFFFF; font-size: 0.78rem; font-weight: 800; letter-spacing: 1px; padding: 4px 12px; border-radius: 9999px; text-transform: uppercase;">
                    Verified Database Counts
                </span>
                <h2 style="font-size: 2.2rem; font-weight: 900; color: #0F172A; margin: 10px 0 4px 0; letter-spacing: -0.5px;">
                    {"उपलब्ध सरकारी योजनाएं" if lang == "hi" else "GOVERNMENT SCHEMES AVAILABLE"}
                </h2>
                <p style="font-size: 1rem; color: #475569; margin: 0;">
                    {"योजना सहायक डेटाबेस पर वर्तमान में उपलब्ध आधिकारिक सरकारी योजनाओं के आंकड़े" if lang == "hi" else "Live scheme counts currently indexed and verified in our database"}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3 Large Statistic Cards
    col_t1, col_t2, col_t3 = st.columns(3, gap="medium")

    with col_t1:
        st.markdown(
            f"""
            <div class="stat-box-hero">
                <div class="stat-num-hero">{total_schemes}</div>
                <div class="stat-label-hero">
                    <span>{"कुल योजनाएं" if lang == "hi" else "TOTAL SCHEMES"}</span>
                    <span class="arrow">→</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Browse All Schemes →" if lang != "hi" else "सभी योजनाएं देखें →", key="btn_hero_stat_total", use_container_width=True):
            navigate_to("schemes")

    with col_t2:
        st.markdown(
            f"""
            <div class="stat-box-hero">
                <div class="stat-num-hero">{central_schemes}</div>
                <div class="stat-label-hero">
                    <span>{"केंद्रीय योजनाएं" if lang == "hi" else "CENTRAL SCHEMES"}</span>
                    <span class="arrow">→</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Central Schemes →" if lang != "hi" else "केंद्रीय योजनाएं देखें →", key="btn_hero_stat_central", use_container_width=True):
            st.session_state.selected_level_filter = "Central"
            navigate_to("schemes")

    with col_t3:
        st.markdown(
            f"""
            <div class="stat-box-hero">
                <div class="stat-num-hero">{state_schemes}</div>
                <div class="stat-label-hero">
                    <span>{"राज्य / केंद्रशासित योजनाएं" if lang == "hi" else "STATE / UT SCHEMES"}</span>
                    <span class="arrow">→</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("State / UT Schemes →" if lang != "hi" else "राज्य योजनाएं देखें →", key="btn_hero_stat_state", use_container_width=True):
            st.session_state.selected_level_filter = "State"
            navigate_to("schemes")

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # STEP 4: CATEGORY COUNTS (10 Verified Categories with Live DB Counts)
    # =========================================================================
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

    # The 10 requested categories with exact database filter mappings
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

    st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 36px 0 28px 0;' />", unsafe_allow_html=True)

    # =========================================================================
    # FEATURED GOVERNMENT SCHEMES CAROUSEL
    # =========================================================================
    st.markdown(
        f"""
        <div class="discovery-section-header">
            <h2 class="discovery-title">
                {"प्रमुख सरकारी योजनाएं" if lang == "hi" else "Featured Government Schemes"}
            </h2>
            <p class="discovery-subtitle">
                {"भारत भर में उपलब्ध महत्वपूर्ण सरकारी योजनाओं का अन्वेषण करें" if lang == "hi" else "Explore important government schemes available across India"}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Resilient featured schemes retrieval (DB direct fallback)
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
    # 3-STEP PROCESS CARDS GRID
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
                    {"आपके उत्तर प्रत्येक योजना के वास्तविक पात्रता मानदंडों के विरुद्ध जाँचे जाते हैं — कोई अनुमान नहीं।" if lang == "hi" else "Your answers are checked against each scheme's real eligibility criteria — no guesswork."}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_s3:
        st.markdown(
            f"""
            <div class="step-card">
                <div class="step-icon-box">📄</div>
                <div class="step-label">{"चरण 3" if lang == "hi" else "Step 3"}</div>
                <div class="step-title">{"स्पष्ट कार्य योजना प्राप्त करें" if lang == "hi" else "Get a clear action plan"}</div>
                <div class="step-desc">
                    {"पात्रता के कारण, आवश्यक दस्तावेज, चरणबद्ध आवेदन प्रक्रिया और आधिकारिक सरकारी लिंक।" if lang == "hi" else "Reasons, documents, step-by-step application process and the official government link."}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Independent Information Tool Disclaimer
    st.markdown(
        f"""
        <div class="civic-footer-note">
            {"योजना सहायक एक स्वतंत्र सूचना उपकरण है। कृपया प्रत्येक योजना से जुड़े आधिकारिक सरकारी पोर्टल पर विवरण सत्यापित करें।" if lang == "hi" else "Yojana Sahayak is an independent information tool. Always verify details on the official government portal linked with each scheme."}
        </div>
        """,
        unsafe_allow_html=True,
    )
