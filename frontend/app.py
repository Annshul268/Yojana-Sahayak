"""Yojana Sahayak - Main Streamlit Application."""

import sys
from pathlib import Path

# Add project root to sys.path to ensure modules can be imported
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from frontend.components.navbar import render_navbar
from frontend.services.api_client import api_client

# Streamlit Page Configuration
st.set_page_config(
    page_title="Yojana Sahayak | योजना सहायक",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Render Global Navigation Bar
render_navbar()

# Sidebar: System Information & Status
with st.sidebar:
    st.markdown("### 🇮🇳 योजना सहायक")
    st.markdown("**AI Government Scheme & Benefits Navigator**")
    st.caption("A trustworthy civic public-service platform for Indian citizens.")
    st.divider()

    st.markdown("#### ⚙️ System Environment")
    st.info(f"**Backend URL:**\n`{api_client.base_url}`")

    st.divider()
    st.markdown("#### 🧭 Architecture Roadmap")
    st.markdown("""
    - ✅ **Phase 0:** Project Foundation *(Active)*
    - ⏳ **Phase 1:** Streamlit UI Foundation
    - ⏳ **Phase 2:** Database & Supabase Auth
    - ⏳ **Phase 3:** Scheme Data Model
    - ⏳ **Phase 4:** Government Data Pipeline
    - ⏳ **Phase 5:** Deterministic Matching Engine
    - ⏳ **Phase 6:** Search & Filters
    - ⏳ **Phase 7:** ChromaDB & RAG Retrieval
    - ⏳ **Phase 8:** Groq / Llama Integration
    """)

# Main Content Area
st.markdown(
    """
    <div style="background: linear-gradient(135deg, #1A365D 0%, #2B6CB0 100%); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; margin-top: 0; font-size: 2rem;">Welcome to Yojana Sahayak (योजना सहायक)</h1>
        <p style="font-size: 1.1rem; opacity: 0.95; max-width: 800px; margin-bottom: 0;">
            Empowering Indian citizens to discover welfare schemes and benefits tailored to their eligibility—backed by verified government data, deterministic rule-matching, and grounded AI explanations.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Backend Connectivity Verification Card (Phase 0 Core Requirement)
st.subheader("🔌 Backend Service Connectivity")
st.write("Verifying live communication: **Streamlit Frontend ➔ FastAPI Backend ➔ /api/health**")

col_action, col_spacer = st.columns([2, 4])
with col_action:
    refresh = st.button("🔄 Test Backend Connection", use_container_width=True)

# Query backend health
health_result = api_client.check_health()

if health_result["ok"]:
    data = health_result["data"]
    st.success("✅ **FastAPI Backend is Connected & Healthy!**")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Backend Status", value=data.get("status", "unknown").upper())
    with col2:
        st.metric(label="Service Name", value=data.get("service", "N/A"))
    with col3:
        st.metric(label="API Version", value=f"v{data.get('version', '0.1.0')}")
    with col4:
        st.metric(label="Environment", value=data.get("environment", "development"))

    with st.expander("🔍 View Raw Health API Response payload", expanded=False):
        st.json(data)
else:
    st.error(f"❌ **Backend Communication Error:** {health_result['error']}")
    st.warning(
        "To start the FastAPI backend server locally:\n"
        "```bash\n"
        "uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000\n"
        "```"
    )

st.divider()

# Core Architecture & Principles Summary
st.subheader("🏛️ Core Principles & Architecture")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown(
        """
        ### ⚖️ The Core Principle: Accuracy First
        - **Source of Truth:** Verified government datasets, structured PostgreSQL records, and deterministic eligibility rules.
        - **Role of AI:** The LLM is **never** the source of truth for government rules or benefit amounts. It serves as an interaction, translation, and grounded explanation layer.
        - **Grounding:** Every recommendation is backed by traceable government sources and official application links.
        """
    )

with col_b:
    st.markdown(
        """
        ### 🏗️ Technology Stack
        - **Frontend:** Streamlit (Python, responsive civic design, bilingual UI)
        - **Backend:** FastAPI (REST endpoints, business logic, matching engine)
        - **Database:** PostgreSQL (structured profile and scheme storage)
        - **Authentication:** Supabase Auth
        - **Vector Store & RAG:** ChromaDB + Sentence Transformers
        - **LLM Engine:** Groq API (Llama models via modular provider)
        """
    )
