"""Home page matching the Lovable civic UI reference screenshots."""

from typing import Callable
import streamlit as st
from frontend.utils.i18n import get_current_language

CATEGORIES_COVERED = [
    ("Education & scholarships", "शिक्षा एवं छात्रवृत्ति"),
    ("Health", "स्वास्थ्य"),
    ("Housing", "आवास"),
    ("Agriculture", "कृषि"),
    ("Business & loans", "व्यवसाय एवं ऋण"),
    ("Employment & skills", "रोजगार एवं कौशल"),
    ("Pension", "पेंशन"),
    ("Insurance", "बीमा"),
    ("Women & child", "महिला एवं बाल विकास"),
    ("Disability support", "दिव्यांगजन सहायता"),
]


def render_home(navigate_to: Callable[[str], None]) -> None:
    lang = get_current_language()

    # Top Section: Two Columns (Left Hero, Right Categories Covered)
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

        # Fine print footnote
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

        # Render clickable category chips
        st.markdown("<div style='margin-top: -12px; margin-bottom: 8px;'>", unsafe_allow_html=True)
        # Render chips in a compact flow grid
        c_row1 = st.columns(2)
        for idx, (cat_en, cat_hi) in enumerate(CATEGORIES_COVERED):
            label = cat_hi if lang == "hi" else cat_en
            with c_row1[idx % 2]:
                if st.button(label, key=f"cat_chip_{idx}", use_container_width=True):
                    # Pre-select category and jump to finder
                    if "finder_answers" not in st.session_state:
                        st.session_state.finder_answers = {}
                    st.session_state.finder_answers["needs"] = [cat_en]
                    navigate_to("finder")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

    # 3-Step Process Cards Grid
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
