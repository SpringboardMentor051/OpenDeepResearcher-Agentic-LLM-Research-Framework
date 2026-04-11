import sys
import os
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import streamlit as st
from milestone3.backend.pipeline_wrapper import run_pipeline
from milestone3.memory.memory import load_chats, save_chats

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from io import BytesIO

st.set_page_config(page_title="OpenDeepResearcher", layout="wide")

st.title("OpenDeepResearcher")

# ---------- SESSION ----------

chats, titles = load_chats()

if "chats" not in st.session_state:
    st.session_state.chats = chats

if "titles" not in st.session_state:
    st.session_state.titles = titles

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

if "menu_chat" not in st.session_state:
    st.session_state.menu_chat = None

if "last_response" not in st.session_state:
    st.session_state.last_response = None

if "last_sources" not in st.session_state:
    st.session_state.last_sources = []

# ---------- PDF ----------

def generate_pdf(text, sources=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        spaceAfter=20
    )

    h2 = styles['Heading2']
    h3 = styles['Heading3']
    h4 = styles['Heading4']
    body = styles['Normal']

    content = []

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        if line.startswith("# "):
            content.append(Paragraph(line.replace("# ", ""), title_style))

        elif line.startswith("## "):
            content.append(Paragraph(line.replace("## ", ""), h2))

        elif line.startswith("### "):
            content.append(Paragraph(line.replace("### ", ""), h3))

        elif line.startswith("#### "):
            content.append(Paragraph(line.replace("#### ", ""), h4))

        elif line.startswith("-"):
            content.append(Paragraph(line[1:].strip(), body))

        else:
            content.append(Paragraph(line, body))

        content.append(Spacer(1, 6))

    # ---------- SOURCES ----------
    if sources:
        content.append(Spacer(1, 20))
        content.append(Paragraph("Sources", h2))

        for s in sources:
            content.append(Paragraph(s["title"], h4))
            content.append(Paragraph(f"<font color='blue'>{s['url']}</font>", body))
            content.append(Spacer(1, 6))

    doc.build(content)
    buffer.seek(0)
    return buffer

# ---------- TITLE ----------

def get_title(chat_id, messages):
    if chat_id in st.session_state.titles:
        return st.session_state.titles[chat_id]

    if not messages:
        return "New Chat"

    return " ".join(messages[0]["content"].split()[:6])

# ---------- SIDEBAR ----------

st.sidebar.title("Conversations")

search = st.sidebar.text_input("Search")

if st.sidebar.button("New Chat"):
    chat_id = str(uuid.uuid4())
    st.session_state.chats[chat_id] = []
    st.session_state.current_chat = chat_id
    save_chats(st.session_state.chats, st.session_state.titles)
    st.rerun()

st.sidebar.markdown("---")

# ---------- CHAT LIST ----------

for chat_id, msgs in st.session_state.chats.items():

    title = get_title(chat_id, msgs)

    if search and search.lower() not in title.lower():
        continue

    col1, col2 = st.sidebar.columns([5, 1])

    with col1:
        if chat_id == st.session_state.current_chat:
            st.markdown(f"**{title}**")
        else:
            if st.button(title, key=f"select_{chat_id}"):
                st.session_state.current_chat = chat_id
                st.rerun()

    with col2:
        if st.button("⋯", key=f"menu_{chat_id}"):
            st.session_state.menu_chat = chat_id

# ---------- MENU ----------

if st.session_state.menu_chat:

    chat_id = st.session_state.menu_chat

    st.sidebar.markdown("---")

    new_name = st.sidebar.text_input("Rename", key=f"rename_{chat_id}")

    if st.sidebar.button("Save", key=f"save_{chat_id}"):
        if new_name.strip():
            st.session_state.titles[chat_id] = new_name

        save_chats(st.session_state.chats, st.session_state.titles)
        st.session_state.menu_chat = None
        st.rerun()

    if st.sidebar.button("Delete", key=f"delete_{chat_id}"):
        if chat_id in st.session_state.chats:
            del st.session_state.chats[chat_id]

        if chat_id in st.session_state.titles:
            del st.session_state.titles[chat_id]

        save_chats(st.session_state.chats, st.session_state.titles)
        st.session_state.current_chat = None
        st.session_state.menu_chat = None
        st.rerun()

# ---------- CREATE CHAT ----------

if st.session_state.current_chat is None:
    chat_id = str(uuid.uuid4())
    st.session_state.current_chat = chat_id
    st.session_state.chats[chat_id] = []
    save_chats(st.session_state.chats, st.session_state.titles)

messages = st.session_state.chats[st.session_state.current_chat]

# ---------- DISPLAY ----------

for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

st.divider()

# ---------- INPUT ----------

user_input = st.chat_input("Ask your research question...")

if user_input:

    messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Generating..."):

            result = run_pipeline(user_input, messages)

            if isinstance(result, dict):
                response = result.get("report", "")
                sources = result.get("sources", [])
            else:
                response = result
                sources = []

            st.markdown(response)

            # ---------- SOURCES UI ----------
            if sources:
                st.markdown("### Sources")
                for s in sources:
                    st.markdown(f"- [{s['title']}]({s['url']})")

            st.session_state.last_sources = sources

    messages.append({"role": "assistant", "content": response})
    st.session_state.last_response = response

    save_chats(st.session_state.chats, st.session_state.titles)

# ---------- DOWNLOAD ----------

if st.session_state.last_response:

    pdf = generate_pdf(
        st.session_state.last_response,
        st.session_state.last_sources
    )

    st.download_button(
        "Download PDF",
        pdf,
        "report.pdf",
        "application/pdf"
    )