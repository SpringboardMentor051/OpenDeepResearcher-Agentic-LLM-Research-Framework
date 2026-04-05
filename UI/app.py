import sys
import os
sys.path.append(os.path.abspath(".."))

import streamlit as st
from main import run_research

# ----------------------
# PAGE CONFIG
# ----------------------
st.set_page_config(page_title="AI Research Assistant", layout="wide")

st.title("🧠 OpenDeepResearcher")

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

for i, msg in enumerate(messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # 🔍 Show research steps (only for assistant messages)
        if msg["role"] == "assistant" and "steps" in msg:

            toggle = st.button("🔍 View Research Process", key=f"toggle_{i}")

            if toggle:
                msg["expanded"] = not msg.get("expanded", False)

            if msg.get("expanded", False):

                # 🧠 Planner Output
                st.markdown("### 🧠 Research Plan")
                for q in msg["steps"].get("planning", []):
                    st.write(f"- {q}")

                # 📊 Intermediate Reasoning
                st.markdown("### 📊 Partial Reasoning")
                for p in msg["steps"].get("partials", []):
                    st.write(p)

# ----------------------
# INPUT
# ----------------------
user_input = st.chat_input("Ask a deep research question...")

if user_input and user_input.strip():

    # Save user message
    messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # ----------------------
    # ASSISTANT RESPONSE
    # ----------------------
    with st.chat_message("assistant"):

        placeholder = st.empty()

        with placeholder.spinner("⏳ Starting research...")
        
        # Extract history (ONLY user messages for backend)
            history = [
                m for m in messages if m["role"] in ["user", "assistant"]
            ]

            try:
                result = run_research(user_input, history[-6:])

                # 🧠 Context awareness
        

                placeholder.markdown("🧠 Planning research...")
                placeholder.markdown("🔍 Searching and analyzing...")
                placeholder.markdown("✍️ Writing report...")

                final_answer = result["final_answer"]

                placeholder.markdown(final_answer)

            except Exception as e:
                final_answer = f"❌ Error: {str(e)}"
                placeholder.markdown(final_answer)

        # Save assistant message with steps
        messages.append({
            "role": "assistant",
            "content": final_answer,
            "steps": result.get("steps", {}) if "result" in locals() else {},
            "expanded": False
        })