"""Navigation bar component for Yojana Sahayak."""

import streamlit as st


def render_navbar() -> None:
    """Renders the top civic navigation banner."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <span style="font-size: 28px;">🏛️</span>
                <div>
                    <h2 style="margin: 0; color: #1A365D; font-weight: 800; font-size: 1.6rem; letter-spacing: -0.5px;">
                        योजना सहायक <span style="font-weight: 400; font-size: 1.2rem; color: #4A5568;">| Yojana Sahayak</span>
                    </h2>
                    <p style="margin: 0; color: #718096; font-size: 0.85rem; font-weight: 500;">
                        AI Government Scheme & Benefits Navigator for Indian Citizens
                    </p>
                </div>
            </div>
            <hr style="margin: 8px 0 20px 0; border: none; border-top: 2px solid #E2E8F0;" />
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div style="text-align: right; padding-top: 8px;">
                <span style="background-color: #FEFCBF; color: #744210; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 700; border: 1px solid #ECC94B;">
                    PHASE 0 : FOUNDATION
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
