import sys
import os
sys.path.append(os.path.abspath(".."))

import streamlit as st
from main import run_research

# ----------------------
# PAGE CONFIG
# ----------------------
st.set_page_config(page_title="AI Research Assistant", layout="wide")

st.title("💬 AI Research Assistant")

# ----------------------
# SESSION INIT
# ----------------------
if "conversations" not in st.session_state:
    st.session_state.conversations = {}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

if st.session_state.current_chat not in st.session_state.conversations:
    st.session_state.conversations[st.session_state.current_chat] = []

# ----------------------
# SIDEBAR
# ----------------------
with st.sidebar:
    st.title("💬 Chats")

    if st.button("➕ New Chat"):
        new_chat = f"Chat {len(st.session_state.conversations) + 1}"
        st.session_state.conversations[new_chat] = []
        st.session_state.current_chat = new_chat
        st.rerun()

    st.divider()

    for chat in list(st.session_state.conversations.keys()):
        if st.button(chat):
            st.session_state.current_chat = chat
            st.rerun()

    st.divider()

    if st.button("🗑 Delete Current Chat"):
        if len(st.session_state.conversations) > 1:
            del st.session_state.conversations[st.session_state.current_chat]
            st.session_state.current_chat = list(st.session_state.conversations.keys())[0]
            st.rerun()
        else:
            st.warning("Cannot delete the only chat")

# ----------------------
# CHAT DISPLAY
# ----------------------
messages = st.session_state.conversations[st.session_state.current_chat]

for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------
# INPUT
# ----------------------
user_input = st.chat_input("Ask anything...")

if user_input and user_input.strip():
    messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Researching..."):
            try:
                response = run_research(user_input, messages)
                
            except Exception as e:
                response = f"❌ Error: {str(e)}"
            st.markdown(response)
   
    messages.append({"role": "assistant", "content": response})

