import streamlit as st
import sys
import os

sys.path.append(os.path.abspath("./agent"))

from agent.planner import plan_query
from agent.searcher import search_web
from agent.writer import generate_answer

st.set_page_config(page_title="Deep Researcher AI", layout="wide")

st.markdown("""
<style>
body { background: linear-gradient(135deg, #1f1c2c, #928dab); }
.block-container { padding-top: 2rem; }
.title { font-size: 42px; font-weight: bold; text-align: center; color: #ffffff; }
.subtitle { text-align: center; color: #dddddd; margin-bottom: 20px; }
.section { padding: 15px; border-radius: 12px; margin-bottom: 15px; }
.plan { background: #2a2a72; color: white; }
.research { background: #009ffd; color: white; }
.answer { background: #00c9a7; color: black; }
</style>
""", unsafe_allow_html=True)

N_DISPLAY = 6
N_CONTEXT = 20

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []

if "active_session_idx" not in st.session_state:
    st.session_state.active_session_idx = None


def get_recent_history(n: int) -> str:
    recent = st.session_state.messages[-n:]
    if not recent:
        return ""
    lines = []
    for msg in recent:
        role = "User" if msg["role"] == "user" else "Assistant"
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines)


def save_current_session():
    if not st.session_state.messages:
        return
    title = next(
        (m["content"][:45] + "…" if len(m["content"]) > 45 else m["content"]
         for m in st.session_state.messages if m["role"] == "user"),
        "Untitled chat",
    )
    session = {"title": title, "messages": list(st.session_state.messages)}
    idx = st.session_state.active_session_idx
    if idx is not None:
        st.session_state.chat_sessions[idx] = session
    else:
        st.session_state.chat_sessions.insert(0, session)
        st.session_state.active_session_idx = 0


def load_session(idx: int):
    st.session_state.messages = list(st.session_state.chat_sessions[idx]["messages"])
    st.session_state.active_session_idx = idx


def start_new_chat():
    save_current_session()
    st.session_state.messages = []
    st.session_state.active_session_idx = None


def run_agent(query: str):
    history = get_recent_history(N_CONTEXT)
    enriched_query = (
        f"Conversation so far:\n{history}\n\nNew question: {query}"
        if history else query
    )

    plan = plan_query(enriched_query)
    questions = plan.get("questions", [query])

    full_context = ""
    research_steps = []
    all_links = []

    for q in questions:
        results = search_web(q)
        research_steps.append(q)

        for item in results:
            full_context += item["content"] + "\n\n"
            all_links.append({
                "title": item["title"],
                "url": item["url"]
            })

    answer = generate_answer(query, full_context)

    return {
        "plan": questions,
        "research": research_steps,
        "answer": answer,
        "links": all_links
    }


with st.sidebar:
    st.markdown("## 🗂 Chat History")

    if st.button("＋ New Chat", use_container_width=True):
        start_new_chat()
        st.rerun()

    st.divider()

    if not st.session_state.chat_sessions:
        st.caption("No past chats yet.")
    else:
        for i, session in enumerate(st.session_state.chat_sessions):
            is_active = (i == st.session_state.active_session_idx)
            label = ("▶ " if is_active else "") + session["title"]
            if st.button(label, key=f"session_{i}", use_container_width=True):
                load_session(i)
                st.rerun()


st.markdown('<div class="title">Deep Researcher AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Planner → Searcher → Writer</div>', unsafe_allow_html=True)

for msg in st.session_state.messages[-N_DISPLAY:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking deeply..."):
            result = run_agent(prompt)

        st.markdown('<div class="section plan"><b>Planned Questions</b></div>', unsafe_allow_html=True)
        for i, step in enumerate(result["plan"], 1):
            st.write(f"{i}. {step}")

        st.markdown('<div class="section research"><b>Research Steps</b></div>', unsafe_allow_html=True)
        for r in result["research"]:
            st.write(f"• {r}")

        st.markdown('<div class="section answer"><b>Final Answer</b></div>', unsafe_allow_html=True)
        st.markdown(result["answer"])

        st.markdown('<div class="section research"><b>Sources</b></div>', unsafe_allow_html=True)

        if result.get("links"):
            for link in result["links"]:
                st.markdown(f"- [{link['title']}]({link['url']})")
        else:
            st.write("No sources found.")

    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
    save_current_session()