import streamlit as st
import json
import os
from opensearch.planner import plan_research
from opensearch.searcher import search
from opensearch.writer import write_report

CHAT_FILE = "chats.json"

#  LOAD 
if "chats" not in st.session_state:
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            st.session_state.chats = json.load(f)
    else:
        st.session_state.chats = {}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New Chat"

if "selected_chat" not in st.session_state:
    st.session_state.selected_chat = None

#  TITLE 
st.set_page_config(page_title="AI Research Assistant", layout="wide")
st.title("🤖 AI Research Assistant")

#  MAIN CHAT 

# Ensure current chat exists
if st.session_state.current_chat not in st.session_state.chats:
    st.session_state.chats[st.session_state.current_chat] = []

messages = st.session_state.chats[st.session_state.current_chat]

# Display messages
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
prompt = st.chat_input("Ask anything...")

if prompt:

    #  AUTO CHAT NAME
    if st.session_state.current_chat == "New Chat" or not messages:
        chat_title = prompt.strip().replace("\n", " ")[:40]

        # Avoid duplicate names
        original = chat_title
        count = 1
        while chat_title in st.session_state.chats:
            chat_title = f"{original} ({count})"
            count += 1

        st.session_state.chats[chat_title] = []
        st.session_state.current_chat = chat_title
        messages = st.session_state.chats[chat_title]

    # Save user message
    messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Processing..."):

            try:
                # Planner 
                questions = plan_research(prompt)
                if not questions:
                    st.error("Planner failed.")
                    st.stop()

                #  Searcher 
                research_data = ""
                for q in questions:
                    result = search(q)
                    if result:
                        research_data += result[:500]

                if not research_data:
                    st.error("Search failed.")
                    st.stop()

                #  Memory 
                recent_messages = messages[-8:]

                # Writer 
                report = write_report(prompt, research_data[:3000], recent_messages)

                if not report:
                    st.error("Writer failed.")
                    st.stop()

                #  Clean 
                report = report.replace("####", "##").replace("###", "##").replace("Subtopic:", "")

                st.markdown(report)

                messages.append({"role": "assistant", "content": report})

                # Save
                with open(CHAT_FILE, "w") as f:
                    json.dump(st.session_state.chats, f)

            except Exception as e:
                st.error(f"Error: {str(e)}")

    st.rerun()

#  SIDEBAR 

st.sidebar.title("💬 Chats")

# ➕ New Chat
if st.sidebar.button("➕ New Chat"):
    st.session_state.current_chat = "New Chat"
    st.rerun()

st.sidebar.markdown("---")

# Show chats
for chat in list(st.session_state.chats.keys()):

    col1, col2 = st.sidebar.columns([5, 1])

    # Open chat
    if col1.button(chat, key=f"open_{chat}"):
        st.session_state.current_chat = chat
        st.rerun()

    # Menu button (⋯)
    if col2.button("⋯", key=f"menu_{chat}"):
        st.session_state.selected_chat = chat

#  OPTIONS PANEL 
if st.session_state.selected_chat:

    st.sidebar.markdown("---")
    st.sidebar.write(f"⚙ Options: {st.session_state.selected_chat}")

    # Rename
    new_name = st.sidebar.text_input("Rename Chat")

    if st.sidebar.button("Rename"):
        if new_name:
            st.session_state.chats[new_name] = st.session_state.chats.pop(st.session_state.selected_chat)

            if st.session_state.current_chat == st.session_state.selected_chat:
                st.session_state.current_chat = new_name

            with open(CHAT_FILE, "w") as f:
                json.dump(st.session_state.chats, f)

            st.session_state.selected_chat = None
            st.rerun()

    # Delete
    if st.sidebar.button("Delete Chat"):
        st.session_state.chats.pop(st.session_state.selected_chat)

        if st.session_state.chats:
            st.session_state.current_chat = list(st.session_state.chats.keys())[0]
        else:
            st.session_state.current_chat = "New Chat"

        with open(CHAT_FILE, "w") as f:
            json.dump(st.session_state.chats, f)

        st.session_state.selected_chat = None
        st.rerun()



if not messages:
    st.info("💡 Start a new conversation...") 
    #streamlit run app.py
    
 