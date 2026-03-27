import sys
import os

# 🔥 fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import streamlit as st
from milestone3.backend.pipeline_wrapper import run_pipeline
from milestone3.memory.memory import load_chats, save_chats

st.set_page_config(page_title="OpenDeepResearcher", layout="wide")

st.title("🤖 OpenDeepResearcher")

# ---------- SESSION STORAGE ----------

if "chats" not in st.session_state:
    st.session_state.chats = load_chats()

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

# ---------- FUNCTION FOR SMART TITLE ----------

def generate_title(messages):
    if not messages:
        return "New Chat"
    
    text = messages[0]["content"]
    words = text.split()
    
    return " ".join(words[:6]) + "..." if len(words) > 6 else text

# ---------- SIDEBAR ----------

st.sidebar.title("💬 Conversations")

# New Chat
if st.sidebar.button("🆕 New Chat"):
    st.session_state.current_chat = None
    st.rerun()

# ---------- CHAT LIST ----------

for chat_id, msgs in st.session_state.chats.items():
    title = generate_title(msgs)

    col1, col2 = st.sidebar.columns([4, 1])

    # select chat
    with col1:
        if chat_id == st.session_state.current_chat:
            st.markdown(f"👉 **{title}**")
        else:
            if st.button(title, key=f"select_{chat_id}"):
                st.session_state.current_chat = chat_id
                st.rerun()

    # delete chat
    with col2:
        if st.button("❌", key=f"delete_{chat_id}"):
            del st.session_state.chats[chat_id]
            save_chats(st.session_state.chats)
            st.session_state.current_chat = None
            st.rerun()

# ---------- CREATE NEW CHAT ----------

if st.session_state.current_chat is None:
    chat_id = f"chat_{len(st.session_state.chats) + 1}"
    st.session_state.current_chat = chat_id
    st.session_state.chats[chat_id] = []

messages = st.session_state.chats[st.session_state.current_chat]

# ---------- DISPLAY CHAT ----------

for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- INPUT ----------

user_input = st.chat_input("Ask your research question...")

if user_input:
    messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run_pipeline(user_input, messages)

            # typing effect (optional but nice)
            placeholder = st.empty()
            full_text = ""
            for word in response.split():
                full_text += word + " "
                placeholder.markdown(full_text)

    messages.append({"role": "assistant", "content": response})

    # save chats permanently
    save_chats(st.session_state.chats)