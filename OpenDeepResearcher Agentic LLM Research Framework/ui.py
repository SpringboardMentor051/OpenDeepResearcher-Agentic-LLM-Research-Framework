import streamlit as st
import json
import os
from datetime import datetime
from main import run_research

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="AI Research Assistant", layout="wide")

HISTORY_FILE = "history.json"


# -----------------------------
# HISTORY FUNCTIONS
# -----------------------------
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_history(history):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except:
        pass


# -----------------------------
# SESSION STATE
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = load_history()

if "topic_input" not in st.session_state:
    st.session_state.topic_input = ""


# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("📜 History")

if st.sidebar.button("🆕 New Research"):
    st.session_state.messages = []
    st.session_state.topic_input = ""

if st.sidebar.button("🗑 Clear History"):
    st.session_state.history = []
    save_history([])
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📌 Recent Searches")

if len(st.session_state.history) == 0:
    st.sidebar.info("No history yet")

else:
    for idx, item in enumerate(reversed(st.session_state.history[-10:])):

        unique_key = f"{item['topic']}_{idx}"

        if st.sidebar.button(
            f"📍 {item['topic']}",
            key=unique_key
        ):

            st.session_state.messages = [
                {"role": "user", "content": item["topic"]},
                {"role": "assistant", "content": item["report"]}
            ]
# -----------------------------
# HEADER
# -----------------------------
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
    <h1 style='font-size:52px; margin-bottom:0px;'>
    🔍 AI Research Assistant
    </h1>
   
    """, unsafe_allow_html=True)




# -----------------------------
# CHAT DISPLAY
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# -----------------------------
# INPUT BOX
# -----------------------------
topic = st.text_input("Enter research topic ➜", key="topic_input")


# -----------------------------
# RUN PIPELINE
# -----------------------------
if topic and topic.strip():

    # show user message
    st.session_state.messages.append({
        "role": "user",
        "content": topic
    })

    with st.chat_message("user"):
        st.write(topic)

    # assistant response
    with st.chat_message("assistant"):

        with st.spinner("🤖 AI Agent is processing..."):
            try:
                report = run_research(topic)
            except Exception as e:
                report = f"⚠️ Error: {str(e)}"

        st.write(report)

    # save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": report
    })

    # -----------------------------
    # SAVE HISTORY (IMPORTANT)
    # -----------------------------
    st.session_state.history.append({
        "topic": topic,
        "report": report,
        
    })

    st.session_state.history = st.session_state.history[-10:]
    save_history(st.session_state.history)

    # -----------------------------
    # RESET INPUT AFTER SEARCH
    # -----------------------------
    st.session_state.topic_input = ""