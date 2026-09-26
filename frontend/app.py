"""Yojana Sahayak - Minimal, Sleek Citizen Service Application."""

import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from frontend.components.navbar import render_navbar
from frontend.pages.admin import render_admin_dashboard
from frontend.pages.home import render_home
from frontend.pages.profile import render_citizen_profile
from frontend.pages.results import render_results
from frontend.pages.saved import render_saved_schemes
from frontend.pages.scheme_details import render_scheme_details
from frontend.pages.scheme_finder import render_scheme_finder
from frontend.pages.schemes import render_schemes_directory
from frontend.pages.tracker import render_application_tracker
from frontend.utils.i18n import get_current_language

# Streamlit Page Configuration - Minimal & Clean
st.set_page_config(
    page_title="Yojana Sahayak | Government Scheme Finder",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Load Custom Minimalist CSS
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
    st.session_state.user_name = "Citizen"
if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = True


def navigate_to(page_name: str) -> None:
    st.session_state["_last_rendered_page"] = st.session_state.get("current_page", "")
    if page_name == "scheme_details":
        st.session_state["_scheme_scroll_to_top"] = True
    st.session_state.current_page = page_name
    st.rerun()


# Direct scheme query parameter navigation (e.g. from featured carousel or direct links)
if "scheme" in st.query_params:
    query_slug = st.query_params.get("scheme")
    if query_slug:
        st.session_state["_last_rendered_page"] = st.session_state.get("current_page", "")
        st.session_state.selected_scheme_slug = query_slug
        st.session_state["_scheme_scroll_to_top"] = True
        st.session_state.current_page = "scheme_details"
    del st.query_params["scheme"]


# Render Clean Top Header with Navigation Tabs
render_navbar(navigate_to)

# Route to Current Page
page = st.session_state.current_page
if page != "scheme_details":
    st.session_state["_last_rendered_page"] = page

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
elif page in ("tracker", "applications"):
    render_application_tracker(navigate_to)
elif page == "profile":
    render_citizen_profile(navigate_to)
elif page == "admin":
    # Protected: Only accessible if is_admin is True
    if st.session_state.get("is_admin", False):
        render_admin_dashboard(navigate_to)
    else:
        st.warning("Staff login required to access Admin Dashboard.")
        if st.button("← Back to Home"):
            navigate_to("home")
else:
    render_home(navigate_to)
