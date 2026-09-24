"""Home page with Featured Schemes Carousel, Live Database Statistics, and Category/State Exploration."""

from typing import Any, Callable, Dict, List
import streamlit as st
from frontend.components.featured_carousel import render_featured_carousel
from frontend.services.api_client import api_client
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
    # SECTION 1 & 2: FEATURED GOVERNMENT SCHEMES CAROUSEL
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

    featured_res = api_client.get_featured_schemes(limit=5)
    featured_schemes: List[Dict[str, Any]] = featured_res.get("data", []) if featured_res["ok"] else []

    if featured_schemes:
        render_featured_carousel(featured_schemes, lang=lang)
    else:
        st.info("Featured schemes are currently loading...")

    st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 32px 0 28px 0;' />", unsafe_allow_html=True)

    # =========================================================================
    # SECTION 5 & 6: SCHEMES AVAILABLE ON YOJANA SAHAYAK (ACTUAL DB STATS)
    # =========================================================================
    st.markdown(
        f"""
        <div class="discovery-section-header">
            <h2 class="discovery-title">
                {"योजना सहायक पर उपलब्ध सरकारी योजनाएं" if lang == "hi" else "Government Schemes Available on Yojana Sahayak"}
            </h2>
            <p class="discovery-subtitle">
                {"हमारे सत्यापित डेटाबेस में उपलब्ध योजनाओं का अन्वेषण करें" if lang == "hi" else "Explore schemes available in our verified database"}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stats_res = api_client.get_scheme_stats()
    stats = stats_res.get("data", {}) if stats_res["ok"] else {
        "total": 438,
        "central": 109,
        "state": 329,
        "categories": {},
        "states": {},
    }

    # 3 Top Statistics Cards
    col_t1, col_t2, col_t3 = st.columns(3, gap="medium")

    with col_t1:
        st.markdown(
            f"""
            <div class="stat-box">
                <div class="stat-num">{stats.get('total', 438)}</div>
                <div class="stat-label">{"कुल योजनाएं" if lang == "hi" else "Total Schemes"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_t2:
        st.markdown(
            f"""
            <div class="stat-box">
                <div class="stat-num">{stats.get('central', 109)}</div>
                <div class="stat-label">{"केंद्रीय योजनाएं" if lang == "hi" else "Central Schemes"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_t3:
        st.markdown(
            f"""
            <div class="stat-box">
                <div class="stat-num">{stats.get('state', 329)}</div>
                <div class="stat-label">{"राज्य योजनाएं" if lang == "hi" else "State Schemes"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # SECTION 7: EXPLORE BY CATEGORY (ACTUAL DB COUNTS)
    # =========================================================================
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 1.25rem;">
            <h3 style="font-size: 1.35rem; font-weight: 800; color: #0F172A; margin-bottom: 4px;">
                {"श्रेणी अनुसार अन्वेषण करें" if lang == "hi" else "Explore by Category"}
            </h3>
            <p style="font-size: 0.88rem; color: #64748B; margin: 0;">
                {"विभिन्न क्षेत्रों में सरकारी योजनाओं की संख्या और विवरण देखें" if lang == "hi" else "Find schemes based on key sectors and target beneficiaries"}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cats_res = api_client.get_scheme_categories()
    categories_list = cats_res.get("data", []) if cats_res["ok"] else []

    if categories_list:
        # Render in a clean 4-column grid
        num_cols = 4
        rows = [categories_list[i : i + num_cols] for i in range(0, len(categories_list), num_cols)]

        for r_idx, row in enumerate(rows):
            cols = st.columns(num_cols, gap="small")
            for c_idx, cat in enumerate(row):
                with cols[c_idx]:
                    cat_name = cat.get("name", "")
                    cat_name_disp = cat.get("name_hi") if lang == "hi" and cat.get("name_hi") else cat_name
                    cat_icon = cat.get("icon", "📋")
                    cat_count = cat.get("count", 0)

                    st.markdown(
                        f"""
                        <div class="cat-tile">
                            <div class="cat-tile-icon">{cat_icon}</div>
                            <div class="cat-tile-name">{cat_name_disp}</div>
                            <div class="cat-tile-count">{cat_count} {"योजनाएं" if lang == "hi" else "Schemes"}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    btn_label = f"देखें ({cat_count})" if lang == "hi" else f"View ({cat_count})"
                    if st.button(btn_label, key=f"btn_cat_view_{r_idx}_{c_idx}", use_container_width=True):
                        st.session_state.selected_category_filter = cat_name
                        navigate_to("schemes")
            st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)

    st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 32px 0 28px 0;' />", unsafe_allow_html=True)

    # =========================================================================
    # SECTION 8 & 9: SCHEMES BY STATE / UT & DYNAMIC STATE FILTER
    # =========================================================================
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 1.25rem;">
            <h3 style="font-size: 1.35rem; font-weight: 800; color: #0F172A; margin-bottom: 4px;">
                {"राज्य / केंद्रशासित प्रदेश अनुसार योजनाएं" if lang == "hi" else "Schemes by State / UT"}
            </h3>
            <p style="font-size: 0.88rem; color: #64748B; margin: 0;">
                {"केंद्रीय योजनाओं के साथ-साथ राज्य सरकार के विशेष कल्याणकारी कार्यक्रमों का अन्वेषण करें" if lang == "hi" else "Explore state welfare programs along with central government schemes"}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    states_res = api_client.get_scheme_states()
    states_list = states_res.get("data", []) if states_res["ok"] else []

    all_state_names = [s["state"] for s in states_list]

    # State Selector Container
    col_sel1, col_sel2 = st.columns([5, 5])
    with col_sel1:
        chosen_state = st.selectbox(
            "Select State / UT" if lang != "hi" else "राज्य / केंद्रशासित प्रदेश चुनें",
            options=["All States"] + all_state_names,
            index=0,
            key="home_state_select_dropdown",
        )

    with col_sel2:
        if chosen_state != "All States":
            # Find specific counts
            st_data = next((s for s in states_list if s["state"] == chosen_state), None)
            st_count = st_data["state_count"] if st_data else 0
            central_cnt = stats.get("central", 109)
            total_app = st_count + central_cnt

            st.markdown(
                f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 14px; font-size: 0.84rem; color: #334155; margin-bottom: 6px;">
                    <strong>{chosen_state}</strong>: {st_count} {"राज्य योजनाएं" if lang == "hi" else "State Schemes"} + {central_cnt} {"केंद्रीय योजनाएं" if lang == "hi" else "Central Schemes"} = <strong>{total_app} {"कुल उपलब्ध" if lang == "hi" else "Total Applicable"}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )
            btn_state_text = f"सभी {total_app} योजनाएं देखें →" if lang == "hi" else f"Browse all {total_app} schemes for {chosen_state} →"
            if st.button(btn_state_text, type="primary", use_container_width=True, key="btn_explore_state_selected"):
                st.session_state.selected_state_filter = chosen_state
                navigate_to("schemes")
        else:
            st.markdown(
                f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 14px; font-size: 0.84rem; color: #334155; margin-bottom: 6px;">
                    {"केंद्रीय योजनाएं संपूर्ण भारत में मान्य हैं।" if lang == "hi" else "Central government schemes are applicable across all States & UTs."}
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Browse All Schemes →" if lang != "hi" else "सभी योजनाएं देखें →", type="secondary", use_container_width=True, key="btn_explore_all_states"):
                navigate_to("schemes")

    # Render Top 10 States with Counts Grid
    if states_list:
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.caption("Top States by Dedicated Welfare Programs in Database:" if lang != "hi" else "डेटाबेस में प्रमुख राज्यों की कल्याणकारी योजनाएं:")

        # Show top 10 states in 5 columns x 2 rows
        top_10 = states_list[:10]
        c_states = st.columns(5)
        for idx, item in enumerate(top_10):
            with c_states[idx % 5]:
                st_name = item["state"]
                st_count = item["state_count"]
                if st.button(f"{st_name}\n({st_count})", key=f"top_state_btn_{idx}", use_container_width=True):
                    st.session_state.selected_state_filter = st_name
                    navigate_to("schemes")

    st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 40px 0 28px 0;' />", unsafe_allow_html=True)

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
