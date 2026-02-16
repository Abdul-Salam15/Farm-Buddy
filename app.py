import streamlit as st
import os
from utils.gemini_api import ask_gemini

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="FarmBuddy - Phase 2",
    page_icon="🌾",
    layout="centered"
)

st.title("🌾 FarmBuddy: Context-Aware Advisor")
st.markdown("### Phase 2: Context-Aware Agricultural Advice")

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- CHAT HISTORY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------- CHAT INPUT ----------------
user_input = st.chat_input("Ask a farming question (e.g., 'How do I plant cassava?')")

if user_input:
    # 1. Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 2. Get AI Response
    with st.chat_message("assistant"):
        with st.spinner("FarmBuddy is thinking..."):
            try:
                # Pass the entire message history to the API with streaming
                # ask_gemini now supports stream=True and handles history internally
                stream = ask_gemini(st.session_state.messages, stream=True)
                
                # Stream the response
                response = st.write_stream(stream)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"⚠️ Error connecting to AI: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
