import streamlit as st
import sys
import os
import re

sys.path.append(os.path.abspath("./agent"))

from agent.planner import plan_query
from agent.searcher import search_web
from agent.writer import WriterAgent

st.set_page_config(page_title="Deep Researcher AI", layout="wide")

# ✅ KEEP WRITER IN SESSION
if "writer" not in st.session_state:
    st.session_state.writer = WriterAgent()

writer = st.session_state.writer

# ---------- STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []

if "active_session_idx" not in st.session_state:
    st.session_state.active_session_idx = None


# ---------- VALIDATION ----------
def is_valid_query(query: str):
    q = query.strip()

    if len(q) < 3:
        return False

    if not re.search(r"[a-zA-Z]", q):
        return False

    return True


# ---------- SAVE / LOAD ----------
def save_current_session():
    if not st.session_state.messages:
        return

    title = st.session_state.messages[0]["content"][:40]

    session = {
        "title": title,
        "messages": list(st.session_state.messages)
    }

    idx = st.session_state.active_session_idx

    if idx is not None:
        st.session_state.chat_sessions[idx] = session
    else:
        st.session_state.chat_sessions.insert(0, session)
        st.session_state.active_session_idx = 0


def load_session(idx):
    st.session_state.messages = list(st.session_state.chat_sessions[idx]["messages"])
    st.session_state.active_session_idx = idx


def new_chat():
    save_current_session()
    st.session_state.messages = []
    st.session_state.active_session_idx = None


# ---------- FOLLOW-UP DETECTION ----------
def is_followup_query(query: str, last_report: str):
    if not last_report:
        return False

    keywords = ["expand", "explain", "more", "detail", "elaborate"]

    if any(k in query.lower() for k in keywords):
        return True

    new_words = set(query.lower().split())
    report_words = set(last_report.lower().split())

    return len(new_words.intersection(report_words)) >= 3


# ---------- AGENT ----------
def run_agent(query: str):
    plan = plan_query(query)
    questions = plan.get("questions", [query])

    context_list = []
    links = []

    for q in questions:
        results = search_web(q)[:3]

        for r in results:
            context_list.append(r["content"])
            links.append({
                "title": r["title"],
                "url": r["url"]
            })

    context = "\n\n".join(context_list)

    MAX_CONTEXT = 12000
    if len(context) > MAX_CONTEXT:
        context = context[:MAX_CONTEXT]

    answer = writer.generate_initial_report(query, context)

    return {
        "plan": questions,
        "research": questions,
        "answer": answer,
        "links": links
    }


# ---------- FOLLOW-UP ----------
def run_followup(query: str):
    context = ""
    MAX_CONTEXT = 8000

    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            context += msg["content"] + "\n"

    if len(context) > MAX_CONTEXT:
        context = context[-MAX_CONTEXT:]

    return writer.handle_follow_up(query, context)


# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("🗂 Research History")

    if st.button("➕ New Chat"):
        new_chat()
        st.rerun()

    st.divider()

    if not st.session_state.chat_sessions:
        st.caption("No history yet")
    else:
        for i, session in enumerate(st.session_state.chat_sessions):
            label = session["title"]
            if st.button(label, key=f"session_{i}"):
                load_session(i)
                st.rerun()


# ---------- UI ----------
st.title("Deep Researcher AI")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask your research question...")


# ---------- MAIN ----------
if prompt:

    # ✅ EDGE CASE FIX
    if not is_valid_query(prompt):
        st.warning("⚠️ Please enter a meaningful research query.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Thinking..."):

            if is_followup_query(prompt, writer.last_generated_report):
                answer = run_followup(prompt)

                result = {
                    "plan": [],
                    "research": [],
                    "answer": answer,
                    "links": []
                }
            else:
                result = run_agent(prompt)

        # OUTPUT
        if result["plan"]:
            st.subheader("🧠 Planned Questions")
            for i, step in enumerate(result["plan"], 1):
                st.write(f"{i}. {step}")

        if result["research"]:
            st.subheader("🔎 Research Steps")
            for r in result["research"]:
                st.write(f"• {r}")

        st.subheader("📄 Final Answer")
        st.markdown(result["answer"])

        if result["links"]:
            st.subheader("🔗 Sources")
            for link in result["links"]:
                st.markdown(f"- [{link['title']}]({link['url']})")

    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})

    # ✅ SAVE SESSION
    save_current_session()