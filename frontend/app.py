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
    st.session_state.user_id = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False


def is_in_callback() -> bool:
    try:
        from streamlit.runtime.state.session_state import ThreadState, RunLocation
        return ThreadState.get().run_location == RunLocation.CALLBACK
    except Exception:
        return False


def navigate_to(page_name: str) -> None:
    cur = st.session_state.get("current_page", "home")
    if cur == page_name and page_name != "scheme_details":
        return
    if cur and cur != page_name:
        if cur != "scheme_details":
            st.session_state["_last_rendered_page"] = cur
    if page_name in ("scheme_details", "scheme_detail"):
        st.session_state["_scheme_scroll_to_top"] = True
        if not st.session_state.get("scheme_navigation_source"):
            SOURCE_INFERENCE = {
                "home": "featured",
                "schemes": "all_schemes",
                "saved": "saved",
                "tracker": "applications",
                "applications": "applications",
                "results": "results",
                "finder": "finder",
                "profile": "profile",
            }
            st.session_state["scheme_navigation_source"] = SOURCE_INFERENCE.get(cur, "featured")
    st.session_state.current_page = page_name
    if not is_in_callback():
        st.rerun()


# Direct scheme query parameter navigation (e.g. from featured carousel or direct links)
if "scheme" in st.query_params:
    query_slug = st.query_params.get("scheme")
    if isinstance(query_slug, list) and query_slug:
        query_slug = query_slug[0]
    if query_slug:
        prev = st.session_state.get("current_page", "home") or "home"
        if prev not in ("scheme_details", "scheme_detail"):
            st.session_state["_last_rendered_page"] = prev
        if not st.session_state.get("scheme_navigation_source"):
            st.session_state["scheme_navigation_source"] = "featured" if prev == "home" else prev
        st.session_state.selected_scheme_slug = str(query_slug).strip()
        st.session_state.selected_scheme_id = str(query_slug).strip()
        st.session_state["_scheme_scroll_to_top"] = True
        st.session_state.current_page = "scheme_details"
    try:
        del st.query_params["scheme"]
    except Exception:
        pass


# Render Clean Top Header with Navigation Tabs
render_navbar(navigate_to)

# Route to Current Page (rendered atomically inside dedicated container)
page = st.session_state.get("current_page", "home")
selected_id = st.session_state.get("selected_scheme_id") or st.session_state.get("selected_scheme_slug")
nav_src = st.session_state.get("scheme_navigation_source") or st.session_state.get("navigation_source")
print(f"\nCURRENT PAGE = {page}\nSELECTED SCHEME ID = {selected_id}\nNAVIGATION SOURCE = {nav_src}\n")

main_slot = st.empty()
main_slot.empty()

with main_slot.container():
    with st.container(key=f"active_page_view_{page}"):
        if page in ("home", "index"):
            render_home(navigate_to)
        elif page in ("finder", "questionnaire"):
            render_scheme_finder(navigate_to)
        elif page in ("results", "matches"):
            render_results(navigate_to)
        elif page in ("schemes", "all_schemes", "directory"):
            render_schemes_directory(navigate_to)
        elif page in ("scheme_details", "scheme_detail"):
            render_scheme_details(navigate_to)
        elif page in ("saved", "saved_schemes"):
            render_saved_schemes(navigate_to)
        elif page in ("tracker", "applications", "my_applications"):
            render_application_tracker(navigate_to)
        elif page in ("profile", "account"):
            render_citizen_profile(navigate_to)
        elif page == "admin":
            # Protected: Only accessible if is_admin is True
            if st.session_state.get("is_admin", False):
                render_admin_dashboard(navigate_to)
            else:
                st.warning("Staff login required to access Admin Dashboard.")
                if st.button("← Back to Home", on_click=navigate_to, args=("home",)):
                    navigate_to("home")
        else:
            render_home(navigate_to)

