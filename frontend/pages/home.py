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
    # 1. TOP ROW: BENEFITS (LEFT) & FEATURED SCHEMES CAROUSEL (RIGHT)
    # Side-by-side on desktop, naturally stacking on mobile
    # =========================================================================
    col_left, col_right = st.columns([5.2, 4.8], gap="large")

    with col_left:
        st.markdown(
            f"""
            <div style="padding: 0; margin: 0;">
                <div class="hero-tag-pill" style="display: inline-flex; margin: 0 0 10px 0;">
                    <span>✓</span>
                    <span>{"वे सरकारी योजनाएं खोजें जिनके लिए आप वास्तव में पात्र हैं" if lang == "hi" else "Find the government schemes you actually qualify for"}</span>
                </div>
                <h1 class="hero-headline" style="font-size: 2.45rem; font-weight: 800; margin: 0 0 12px 0; line-height: 1.2; text-align: left;">
                    {"सरकारी लाभ, सरल भाषा में समझें" if lang == "hi" else "Government benefits, explained in plain language"}
                </h1>
                <p class="hero-subhead" style="font-size: 1.05rem; line-height: 1.6; margin: 0 0 18px 0; text-align: left; max-width: 100%;">
                    {"अपने बारे में कुछ सरल प्रश्नों के उत्तर दें। हम आधिकारिक केंद्रीय एवं राज्य योजनाओं के साथ आपके विवरण का मिलान करते हैं और बताते हैं कि आप क्यों पात्र हैं, कौन से दस्तावेज चाहिए, और आवेदन कैसे करें।" if lang == "hi" else "Answer a few simple questions about yourself. We match you against official central and state schemes and tell you why you qualify, which documents you need, and exactly how to apply."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_b1, col_b2 = st.columns([1.1, 1], gap="small")
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
            <div class="hero-footnote" style="text-align: left; margin-top: 12px; margin-bottom: 6px;">
                {"प्रत्येक परिणाम आधिकारिक सरकारी स्रोत से जुड़ा है। हम कभी कोई योजना नहीं बनाते।" if lang == "hi" else "Every result links to an official government source. We never invent a scheme."}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown(
            f"""
            <div class="hero-carousel-header" style="text-align: left; margin: 0 0 8px 0; padding: 0;">
                <h2 class="discovery-title" style="font-size: 1.12rem; font-weight: 800; color: #1E3A8A; margin: 0 0 4px 0; letter-spacing: 0.04em; text-transform: uppercase;">
                    {"प्रमुख सरकारी योजनाएं" if lang == "hi" else "FEATURED GOVERNMENT SCHEMES"}
                </h2>
                <p class="discovery-subtitle" style="font-size: 0.90rem; color: #475569; margin: 0; line-height: 1.4;">
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

    st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 34px 0 28px 0;' />", unsafe_allow_html=True)

    # =========================================================================
    # 3. SCHEME COUNTERS (Total Schemes | Central Schemes | State/UT Schemes)
    # =========================================================================
    stats = get_live_db_statistics()
    total_schemes = stats.get("total", 438)
    central_schemes = stats.get("central", 109)
    state_schemes = stats.get("state", 329)

    col_c1, col_c2, col_c3 = st.columns(3, gap="medium")

    with col_c1:
        st.markdown(
            f"""
            <div class="stat-box-hero">
                <div class="stat-num-hero">{total_schemes}+</div>
                <div class="stat-label-hero">
                    <span>{"कुल योजनाएं" if lang == "hi" else "Total Schemes"}</span>
                    <span class="arrow">→</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("All Schemes →" if lang != "hi" else "सभी योजनाएं देखें →", key="btn_ctr_total", use_container_width=True):
            navigate_to("schemes")

    with col_c2:
        st.markdown(
            f"""
            <div class="stat-box-hero">
                <div class="stat-num-hero">{central_schemes}+</div>
                <div class="stat-label-hero">
                    <span>{"केंद्रीय योजनाएं" if lang == "hi" else "Central Schemes"}</span>
                    <span class="arrow">→</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Central Schemes →" if lang != "hi" else "केंद्रीय योजनाएं देखें →", key="btn_ctr_central", use_container_width=True):
            st.session_state.selected_level_filter = "Central"
            navigate_to("schemes")

    with col_c3:
        st.markdown(
            f"""
            <div class="stat-box-hero">
                <div class="stat-num-hero">{state_schemes}+</div>
                <div class="stat-label-hero">
                    <span>{"राज्य / केंद्रशासित योजनाएं" if lang == "hi" else "State/UT Schemes"}</span>
                    <span class="arrow">→</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("State/UT Schemes →" if lang != "hi" else "राज्य योजनाएं देखें →", key="btn_ctr_state", use_container_width=True):
            st.session_state.selected_level_filter = "State"
            navigate_to("schemes")

    st.markdown("<div style='height: 1.75rem;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # 4. DISCOVERY TABS: Categories | States/UTs | Central Ministries
    # =========================================================================
    tab_cat, tab_states, tab_min = st.tabs(
        ["Categories", "States/UTs", "Central Ministries"]
        if lang != "hi"
        else ["श्रेणियां", "राज्य / केंद्रशासित प्रदेश", "केंद्रीय मंत्रालय"]
    )

    # TAB 1: Categories
    with tab_cat:
        st.markdown(
            f"""
            <div style="margin-top: 10px; margin-bottom: 20px;">
                <h3 style="font-size: 1.35rem; font-weight: 800; color: #0F172A; margin-bottom: 3px;">
                    {"श्रेणियों के आधार पर योजनाएं खोजें" if lang == "hi" else "Find schemes based on categories"}
                </h3>
                <p style="font-size: 0.92rem; color: #64748B; margin: 0;">
                    {"विभिन्न श्रेणियों में उपलब्ध सरकारी योजनाओं की संख्या देखें" if lang == "hi" else "Explore welfare programs curated by key sectors in our database"}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        category_items = stats.get("category_items", [])
        if category_items:
            num_cols = 4
            cat_rows = [category_items[i : i + num_cols] for i in range(0, len(category_items), num_cols)]

            for r_idx, row in enumerate(cat_rows):
                cols = st.columns(num_cols, gap="small")
                for c_idx, item in enumerate(row):
                    with cols[c_idx]:
                        cat_name = item["name"]
                        disp_name = item["name_hi"] if lang == "hi" and item.get("name_hi") else cat_name
                        icon = item.get("icon", "📋")
                        count = item.get("count", 0)

                        st.markdown(
                            f"""
                            <div class="cat-card-modern">
                                <div class="cat-icon-badge">{icon}</div>
                                <div class="cat-schemes-count">{count} {"योजनाएं" if lang == "hi" else "Schemes"}</div>
                                <div class="cat-card-title">{disp_name}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        btn_label = f"देखें ({count})" if lang == "hi" else f"Explore ({count}) →"
                        if st.button(btn_label, key=f"btn_tab_cat_{r_idx}_{c_idx}", use_container_width=True):
                            st.session_state.selected_category_filter = item["db_category"]
                            navigate_to("schemes")
                st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # TAB 2: States/UTs
    with tab_states:
        st.markdown(
            f"""
            <div style="margin-top: 10px; margin-bottom: 20px;">
                <h3 style="font-size: 1.35rem; font-weight: 800; color: #0F172A; margin-bottom: 3px;">
                    {"राज्यों और केंद्रशासित प्रदेशों के आधार पर योजनाएं खोजें" if lang == "hi" else "Find schemes based on states and union territories"}
                </h3>
                <p style="font-size: 0.92rem; color: #64748B; margin: 0;">
                    {"राज्य-विशिष्ट सरकारी कल्याणकारी योजनाओं का अन्वेषण करें" if lang == "hi" else "Explore state-specific welfare programs currently available in our database"}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        states_list = stats.get("states", [])
        if states_list:
            num_cols = 2
            half = (len(states_list) + 1) // 2
            col_st_left, col_st_right = st.columns(num_cols, gap="medium")

            for idx, item in enumerate(states_list):
                st_name = item["state"]
                st_count = item["state_count"]
                target_col = col_st_left if idx < half else col_st_right

                with target_col:
                    c_info, c_btn = st.columns([7, 3])
                    with c_info:
                        st.markdown(
                            f"""
                            <div class="state-stat-card">
                                <span class="state-stat-name">{st_name}</span>
                                <span class="state-stat-pill">{st_count} {"योजनाएं" if lang == "hi" else "Schemes"}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with c_btn:
                        if st.button("Explore →" if lang != "hi" else "देखें →", key=f"btn_tab_state_{idx}", use_container_width=True):
                            st.session_state.selected_state_filter = st_name
                            navigate_to("schemes")

    # TAB 3: Central Ministries
    with tab_min:
        st.markdown(
            f"""
            <div style="margin-top: 10px; margin-bottom: 20px;">
                <h3 style="font-size: 1.35rem; font-weight: 800; color: #0F172A; margin-bottom: 3px;">
                    {"केंद्रीय मंत्रालयों और विभागों के आधार पर योजनाएं खोजें" if lang == "hi" else "Find schemes based on central government ministries"}
                </h3>
                <p style="font-size: 0.92rem; color: #64748B; margin: 0;">
                    {"विभिन्न केंद्रीय मंत्रालयों द्वारा संचालित राष्ट्रीय कल्याणकारी योजनाएं" if lang == "hi" else "Central schemes organized by implementing ministries and departments"}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        ministries_list = stats.get("ministries", [])
        if ministries_list:
            num_cols = 2
            half = (len(ministries_list) + 1) // 2
            col_min_left, col_min_right = st.columns(num_cols, gap="medium")

            for idx, item in enumerate(ministries_list):
                m_name = item["ministry"]
                m_count = item["count"]
                target_col = col_min_left if idx < half else col_min_right

                with target_col:
                    c_info, c_btn = st.columns([7, 3])
                    with c_info:
                        st.markdown(
                            f"""
                            <div class="state-stat-card">
                                <span class="state-stat-name">{m_name}</span>
                                <span class="state-stat-pill">{m_count} {"योजनाएं" if lang == "hi" else "Schemes"}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with c_btn:
                        if st.button("Explore →" if lang != "hi" else "देखें →", key=f"btn_tab_min_{idx}", use_container_width=True):
                            st.session_state.selected_level_filter = "Central"
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
