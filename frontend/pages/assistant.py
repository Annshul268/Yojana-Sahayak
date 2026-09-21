"""AI Scheme Assistant conversational view."""

from typing import Callable
import streamlit as st
from frontend.services.api_client import api_client
from frontend.utils.i18n import get_current_language, t

SUGGESTED_QUESTIONS = [
    "What documents are required for PM-KISAN registration?",
    "Who is eligible for Ayushman Bharat PM-JAY health card?",
    "What are the loan limits under Pradhan Mantri Mudra Yojana?",
    "What is the interest rate and age limit for Sukanya Samriddhi Yojana?",
    "How does Atal Pension Yojana monthly pension work after age 60?",
]


def render_ai_assistant(navigate_to: Callable[[str], None]) -> None:
    lang = get_current_language()
    st.markdown("## 🤖 " + t("nav_assistant", "AI Scheme Assistant"))
    st.caption("Ask questions about government schemes, eligibility rules, and required documents. Every response is strictly grounded in verified official sources.")

    st.markdown("##### 💡 Suggested Questions")
    cols = st.columns(len(SUGGESTED_QUESTIONS))
    selected_query = None
    for idx, q_text in enumerate(SUGGESTED_QUESTIONS):
        with cols[idx]:
            if st.button(f"📌 {q_text[:35]}...", key=f"sug_{idx}", help=q_text, use_container_width=True):
                selected_query = q_text

    # Conversation state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("references"):
                with st.expander("🔗 Grounded Official Sources"):
                    for ref in msg["references"]:
                        url = ref.get("official_url", "#")
                        cat = ref.get("category", "")
                        st.markdown(f"- [{url}]({url}) ({cat})")

    # Handle user query input
    user_input = st.chat_input("Ask any question about government schemes and benefits...")
    query_to_process = selected_query or user_input

    if query_to_process:
        # Add user query to history
        st.session_state.chat_history.append({"role": "user", "content": query_to_process})
        with st.chat_message("user"):
            st.markdown(query_to_process)

        # Generate grounded response
        with st.chat_message("assistant"):
            with st.spinner("Searching verified government records..."):
                res = api_client.ask_ai(question=query_to_process, language=lang)
                if res["ok"]:
                    answer = res["data"]["answer"]
                    refs = res["data"].get("grounded_references", [])
                    st.markdown(answer)
                    if refs:
                        with st.expander("🔗 Grounded Official Sources"):
                            for ref in refs:
                                url = ref.get("official_url", "#")
                                cat = ref.get("category", "")
                                st.markdown(f"- [{url}]({url}) ({cat})")
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "references": refs,
                    })
                else:
                    err_msg = f"Sorry, could not process request: {res['error']}"
                    st.error(err_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": err_msg})
