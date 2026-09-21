"""Home page for Yojana Sahayak."""

import streamlit as st
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language, t


def render_home(navigate_to) -> None:
    lang = get_current_language()

    # Hero Banner
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #1A365D 0%, #2A4365 50%, #1A202C 100%); color: white; padding: 2.5rem; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="display: inline-block; background: #DD6B20; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px;">
                🇮🇳 Official Citizen Welfare Navigator
            </div>
            <h1 style="color: white; margin-top: 0; font-size: 2.3rem; font-weight: 800; line-height: 1.2;">
                Find Government Schemes & Benefits Designed for You
            </h1>
            <p style="font-size: 1.15rem; opacity: 0.9; max-width: 820px; line-height: 1.6; margin-bottom: 1.8rem;">
                Discover central and state government welfare initiatives tailored to your age, income, state, and occupation. Backed by verified government records and deterministic eligibility checking.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_btn1, col_btn2, col_btn3, col_space = st.columns([3, 3, 3, 2])
    with col_btn1:
        if st.button("🚀 " + t("btn_find_schemes", "Find Schemes for Me"), type="primary", use_container_width=True):
            navigate_to("finder")
    with col_btn2:
        if st.button("📚 " + t("btn_browse_schemes", "Browse Scheme Directory"), use_container_width=True):
            navigate_to("schemes")
    with col_btn3:
        if st.button("🤖 Ask AI Scheme Assistant", use_container_width=True):
            navigate_to("assistant")

    st.markdown("<br>", unsafe_allow_html=True)

    # Core Trust & Accuracy Guarantee Banner
    st.markdown(
        f"""
        <div style="background: #F7FAFC; border: 1px solid #CBD5E0; border-left: 5px solid #DD6B20; border-radius: 8px; padding: 1.25rem; margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                <span style="font-size: 24px;">🛡️</span>
                <h4 style="margin: 0; color: #1A365D; font-size: 1.1rem; font-weight: 700;">
                    {t('trust_banner_title', 'Verified Government Sources First')}
                </h4>
            </div>
            <p style="color: #4A5568; font-size: 0.92rem; line-height: 1.5; margin: 0;">
                {t('trust_banner_desc', 'All information is verified against official government portals. The LLM acts as an explanatory layer and never hallucinates government benefits or eligibility criteria.')}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Key Pillars
    st.markdown("### 🏛️ Why Yojana Sahayak?")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.25rem; height: 100%;">
                <div style="font-size: 26px; margin-bottom: 8px;">🎯</div>
                <h4 style="color: #1A365D; margin-top: 0;">Deterministic Rules</h4>
                <p style="color: #4A5568; font-size: 0.9rem; line-height: 1.5;">
                    Your eligibility is calculated using transparent rule evaluation across state, income ceilings, age brackets, and social categories—not subjective LLM guesses.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.25rem; height: 100%;">
                <div style="font-size: 26px; margin-bottom: 8px;">🔗</div>
                <h4 style="color: #1A365D; margin-top: 0;">Traceable Portals</h4>
                <p style="color: #4A5568; font-size: 0.9rem; line-height: 1.5;">
                    Every scheme includes verified official government links, documentation checklists, and step-by-step application guidance.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.25rem; height: 100%;">
                <div style="font-size: 26px; margin-bottom: 8px;">🗣️</div>
                <h4 style="color: #1A365D; margin-top: 0;">Bilingual & Accessible</h4>
                <p style="color: #4A5568; font-size: 0.9rem; line-height: 1.5;">
                    Full localization in both हिन्दी and English, paired with grounded Groq Llama explanations to simplify bureaucratic guidelines.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
