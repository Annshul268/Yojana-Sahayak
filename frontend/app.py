"""Yojana Sahayak - Main Streamlit Application."""

import sys
from pathlib import Path

# Add project root to sys.path to ensure modules can be imported
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from frontend.components.navbar import render_navbar
from frontend.pages.admin import render_admin_dashboard
from frontend.pages.assistant import render_ai_assistant
from frontend.pages.home import render_home
from frontend.pages.profile import render_citizen_profile
from frontend.pages.results import render_results
from frontend.pages.saved import render_saved_schemes
from frontend.pages.scheme_details import render_scheme_details
from frontend.pages.scheme_finder import render_scheme_finder
from frontend.pages.schemes import render_schemes_directory
from frontend.pages.tracker import render_application_tracker
from frontend.services.api_client import api_client
from frontend.utils.i18n import t

# Streamlit Page Configuration
st.set_page_config(
    page_title="Yojana Sahayak | योजना सहायक",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply Custom CSS styling
css_path = ROOT_DIR / "frontend" / "styles" / "main.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Session state initialization
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "user_id" not in st.session_state:
    st.session_state.user_id = "citizen_user_1"
if "user_name" not in st.session_state:
    st.session_state.user_name = "Aadhaar Citizen"
if "lang" not in st.session_state:
    st.session_state.lang = "en"


def navigate_to(page_name: str) -> None:
    st.session_state.current_page = page_name
    st.rerun()


# Top Navbar
render_navbar()

# Navigation Mapping
NAV_ITEMS = {
    "home": ("🏠", t("nav_home", "Home")),
    "finder": ("🎯", t("nav_finder", "Find Schemes")),
    "results": ("📊", "My Results"),
    "schemes": ("📚", t("nav_schemes", "Browse Schemes")),
    "saved": ("⭐", t("nav_saved", "Saved Schemes")),
    "tracker": ("📈", t("nav_tracker", "Application Tracker")),
    "assistant": ("🤖", t("nav_assistant", "AI Assistant")),
    "profile": ("👤", t("nav_profile", "My Profile")),
    "admin": ("⚙️", t("nav_admin", "Admin Dashboard")),
}

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🇮🇳 Navigation")
    current_key = st.session_state.current_page
    if current_key == "scheme_details":
        current_key = "schemes"

    for page_key, (icon, label) in NAV_ITEMS.items():
        is_active = st.session_state.current_page == page_key
        button_type = "primary" if is_active else "secondary"
        if st.button(f"{icon} {label}", key=f"nav_btn_{page_key}", type=button_type, use_container_width=True):
            navigate_to(page_key)

    st.divider()
    st.markdown("#### ⚡ System Status")
    health = api_client.check_health()
    if health["ok"]:
        st.success("🟢 Backend: Healthy")
    else:
        st.error("🔴 Backend: Disconnected")
    st.caption(f"Backend URL: `{api_client.base_url}`")

# Route Page Rendering
page = st.session_state.current_page

if page == "home":
    render_home(navigate_to)
elif page == "finder":
    render_scheme_finder(navigate_to)
elif page == "results":
    render_results(navigate_to)
elif page == "schemes":
    render_schemes_directory(navigate_to)
elif page == "scheme_details":
    render_scheme_details(navigate_to)
elif page == "saved":
    render_saved_schemes(navigate_to)
elif page == "tracker":
    render_application_tracker(navigate_to)
elif page == "assistant":
    render_ai_assistant(navigate_to)
elif page == "profile":
    render_citizen_profile(navigate_to)
elif page == "admin":
    render_admin_dashboard(navigate_to)
else:
    render_home(navigate_to)
