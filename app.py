import streamlit as st
import json
import os
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from tavily import TavilyClient
from dotenv import load_dotenv

from opensearch.planner import plan_research
from opensearch.writer import write_report

# Load environment variables
load_dotenv()

CHAT_FILE = "chats.json"

# Secure Tavily API
tavily = TavilyClient(api_key=os.getenv("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"))

# PDF FUNCTION 
def generate_pdf(text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    content = []
    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))

    doc.build(content)
    buffer.seek(0)
    return buffer

# LOAD CHAT MEMORY
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

# UI
st.set_page_config(page_title="AI Research Assistant", layout="wide")
st.title("🤖 AI Research Assistant")

# MAIN CHAT
if st.session_state.current_chat not in st.session_state.chats:
    st.session_state.chats[st.session_state.current_chat] = []

messages = st.session_state.chats[st.session_state.current_chat]

# DISPLAY MESSAGES
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if "sources" in msg:
            st.markdown("### 🔗 Sources")
            for i, (title, url) in enumerate(msg["sources"], 1):
                st.markdown(f"{i}. [{title}]({url})")

prompt = st.chat_input("Ask anything...")

if prompt:

    # Auto chat naming
    if st.session_state.current_chat == "New Chat" or not messages:
        chat_title = prompt.strip().replace("\n", " ")[:40]

        original = chat_title
        count = 1
        while chat_title in st.session_state.chats:
            chat_title = f"{original} ({count})"
            count += 1

        st.session_state.chats[chat_title] = []
        st.session_state.current_chat = chat_title
        messages = st.session_state.chats[chat_title]

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

                research_data = ""
                sources = []

                st.subheader("🔎 Retrieved Information")

                for q in questions:
                    try:
                        response = tavily.search(
                            query=q,
                            max_results=3,
                            search_depth="advanced"
                        )

                        for res in response.get("results", []):
                            title = res.get("title", "")
                            content = res.get("content", "")
                            url = res.get("url", "")

                            # Filter bad results
                            if "instagram" in url.lower() or "login" in url.lower():
                                continue

                            if len(content) < 100:
                                continue

                            # UI display
                            st.markdown(f"**🔹 {title}**")
                            st.write(content[:900])
                            st.markdown("---")

                            # Save data
                            research_data += f"{title}\n{content[:1000]}\n\n"
                            sources.append((title, url))

                    except Exception:
                        st.warning(f"Tavily failed for: {q}")

                if not research_data:
                    st.error("No valid research data found.")
                    st.stop()

                # Show sources
                st.markdown("### 🔗 Sources")
                for i, (title, url) in enumerate(sources, 1):
                    st.markdown(f"{i}. [{title}]({url})")

                # Memory
                recent_messages = messages[-8:]

                # Writer
                report = write_report(prompt, research_data[:3000], recent_messages)
                if not report:
                    st.error("Writer failed.")
                    st.stop()

                report = report.replace("####", "##").replace("###", "##")

                st.markdown(report)

                # Save report
                st.session_state["last_report"] = report

                messages.append({
                    "role": "assistant",
                    "content": report,
                    "sources": sources
                })

                with open(CHAT_FILE, "w") as f:
                    json.dump(st.session_state.chats, f)

            except Exception as e:
                st.error(f"Error: {str(e)}")

# PDF DOWNLOAD
if "last_report" in st.session_state:
    pdf_file = generate_pdf(st.session_state["last_report"])

    st.download_button(
        label="📄 Download Report as PDF",
        data=pdf_file,
        file_name="research_report.pdf",
        mime="application/pdf"
    )

# SIDEBAR
st.sidebar.title("💬 Chats")

if st.sidebar.button("➕ New Chat"):
    st.session_state.current_chat = "New Chat"
    st.rerun()

st.sidebar.markdown("---")

for chat in list(st.session_state.chats.keys()):
    col1, col2 = st.sidebar.columns([5, 1])

    if col1.button(chat, key=f"open_{chat}"):
        st.session_state.current_chat = chat
        st.rerun()

    if col2.button("⋯", key=f"menu_{chat}"):
        st.session_state.selected_chat = chat

if st.session_state.selected_chat:

    st.sidebar.markdown("---")
    st.sidebar.write(f"⚙ Options: {st.session_state.selected_chat}")

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
  
