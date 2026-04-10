"""Streamlit UI for the Open Researcher Project.

This app provides a ChatGPT-like interface for running the research pipeline
from `pipeline.execute_research`.

Features:
- Input prompt + result display
- Session memory persisted to disk
- Thread tracking + continuity support
- Clean chat-like UI styling
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime

# Ensure local module imports work when running via `streamlit run`.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import streamlit as st

from pipeline import execute_research


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def _get_storage_path(filename: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, filename)


SESSIONS_FILE = _get_storage_path("streamlit_sessions.json")


def load_sessions() -> dict:
    """Load saved sessions from disk."""
    try:
        if os.path.exists(SESSIONS_FILE):
            with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f) or {}
    except Exception:
        # If the file is corrupt or unreadable, start fresh
        pass
    return {"sessions": []}


def save_sessions(data: dict) -> None:
    """Persist sessions to disk."""
    try:
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        # best-effort persistence; ignore on failure
        pass


def format_results(result: dict) -> str:
    """Format pipeline results for display in the chat UI."""
    if result.get("error"):
        return f"⚠️ Error: {result.get('error')}"
    
    text_chunks = []
    
    if result.get("summary") and result["summary"].get("summary"):
        text_chunks.append(result["summary"].get("summary"))
    else:
        text_chunks.append("No final answer could be generated.")
        
    search_data = result.get("search_results")
    if search_data and isinstance(search_data, dict):
        search_list = search_data.get("search_results", [])
        if search_list and len(search_list) > 0:
            text_chunks.append("\n### 📚 Sources")
            for group in search_list:
                if isinstance(group, dict) and "results" in group:
                    for src in group["results"]:
                        if isinstance(src, dict):
                            title = src.get("title", src.get("url", "Source"))
                            url = src.get("url", "#")
                            text_chunks.append(f"- [{title}]({url})")
                        else:
                            text_chunks.append(f"- {str(src)}")
                else:
                    text_chunks.append(f"- {str(group)}")
    
    return "\n".join(text_chunks)


def create_thread(topic: str) -> dict:
    """Create a new thread object."""
    now = datetime.utcnow().isoformat() + "Z"
    return {
        "id": str(uuid.uuid4()),
        "created_at": now,
        "last_updated": now,
        "topic": topic.strip(),
        "history": [],
        "result": None,
    }


def add_history(session: dict, role: str, message: str) -> None:
    """Append a message to the session history."""
    session["history"].append(
        {
            "role": role,
            "text": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    )
    session["last_updated"] = datetime.utcnow().isoformat() + "Z"


def render_chat(session: dict) -> None:
    """Render chat bubbles for a session."""
    st.markdown(
        """
        <style>
        .chat-container { padding: 0 0.5rem; }
        .user-bubble { background: rgba(0, 123, 255, 0.12); padding: 12px 14px; border-radius: 18px; margin: 8px 0; text-align: right; }
        .assistant-bubble { background: rgba(40, 40, 40, 0.08); padding: 12px 14px; border-radius: 18px; margin: 8px 0; text-align: left; }
        .chat-meta { font-size: 0.8rem; color: #666; margin-bottom: 0.35rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Show only the last 5 conversations (10 messages)
    history_to_show = session.get("history", [])[-10:]
    for message in history_to_show:
        role = message.get("role")
        text = message.get("text", "")
        timestamp = message.get("timestamp", "")

        if role == "user":
            st.markdown(
                f"<div class='chat-container'>"
                f"<div class='chat-meta'>You • {timestamp}</div>"
                f"<div class='user-bubble'>{text}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div class='chat-container'>"
                f"<div class='chat-meta'>Assistant • {timestamp}</div>"
                f"<div class='assistant-bubble'>{text}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )


def main() -> None:
    st.set_page_config(
        page_title="Open Researcher",
        page_icon="🤖",
        layout="wide",
    )

    st.title("🤖 Open Researcher")
    st.caption("A ChatGPT-style interface for the LangGraph research pipeline")

    # Load sessions into streamlit state
    if "sessions" not in st.session_state:
        st.session_state.sessions = load_sessions().get("sessions", [])

    if "active_thread_id" not in st.session_state:
        st.session_state.active_thread_id = None

    # Sidebar - Thread selection and actions
    with st.sidebar:
        st.header("Threads")

        existing = {s["id"]: f"{s['topic']} (updated {s['last_updated'][:19]})" for s in st.session_state.sessions}
        thread_ids = list(existing.keys())

        # Guard against stale active_thread_id causing index errors
        if st.session_state.active_thread_id not in thread_ids:
            st.session_state.active_thread_id = None

        selected_index = 0
        if st.session_state.active_thread_id is not None:
            try:
                selected_index = thread_ids.index(st.session_state.active_thread_id) + 1
            except ValueError:
                selected_index = 0
                st.session_state.active_thread_id = None

        selected = st.selectbox(
            "Select thread",
            options=["_new_"] + thread_ids,
            format_func=lambda x: "Start new thread" if x == "_new_" else existing.get(x, ""),
            index=selected_index,
        )

        if selected == "_new_":
            st.session_state.active_thread_id = None
        else:
            st.session_state.active_thread_id = selected

        st.markdown("---")
        if st.button("🧹 Clear all threads"):
            st.session_state.sessions = []
            st.session_state.active_thread_id = None
            save_sessions({"sessions": st.session_state.sessions})
            st.rerun()

        st.markdown("---")
        st.markdown("💡 Tip: Use the input below to run research or follow up on existing threads.")

    # Determine current thread
    active_thread = None
    if st.session_state.active_thread_id:
        for thread in st.session_state.sessions:
            if thread["id"] == st.session_state.active_thread_id:
                active_thread = thread
                break

    is_new_thread = active_thread is None

    # Input area
    with st.form("prompt_form", clear_on_submit=False):
        if is_new_thread:
            prompt = st.text_input("Research topic or question", key="topic_input")
            st.write(
                "🔁 Each input will run the full research pipeline; follow-ups can be added to an existing thread."
            )
        else:
            prompt = st.text_input(
                "Ask a follow-up or refine the topic",
                key="followup_input",
                value="",
            )
            st.checkbox(
                "Treat this as a new topic (reset thread)", key="reset_thread_checkbox"
            )

        submit = st.form_submit_button("🚀 Run Research")

    if submit and prompt:
        user_display_prompt = prompt
        
        if is_new_thread or st.session_state.get("reset_thread_checkbox"):
            active_thread = create_thread(prompt)
            st.session_state.sessions.insert(0, active_thread)
            st.session_state.active_thread_id = active_thread["id"]
            research_prompt = prompt
        else:
            # Append follow-up to topic for continuity
            research_prompt = f"{active_thread['topic']}\nFollow-up: {prompt}"

        add_history(active_thread, "user", user_display_prompt)

        with st.spinner("Running research pipeline (this may take a minute)..."):
            try:
                result = execute_research(research_prompt)
            except Exception as exc:
                result = {
                    "topic": prompt,
                    "status": "failed",
                    "error": f"Unhandled exception: {exc}",
                    "plan": None,
                    "search_results": None,
                    "summary": None,
                    "execution_time": 0,
                }

        assistant_text = format_results(result)
        add_history(active_thread, "assistant", assistant_text)
        active_thread["result"] = result

        save_sessions({"sessions": st.session_state.sessions})
        st.rerun()

    # Display active thread
    if active_thread:
        st.subheader(f"Thread: {active_thread['topic']}")
        render_chat(active_thread)

        # We no longer display the raw JSON, pipeline logs, or duplicate assistant text
        # as the user requested a chatbot-like experience focusing only on the answer.


    else:
        st.info("Start a new thread by entering a topic above and clicking Run Research.")


if __name__ == "__main__":
    main()
