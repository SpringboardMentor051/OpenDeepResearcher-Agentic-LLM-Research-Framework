import sys
import time
import socket
import json
from importlib import import_module
from pathlib import Path
from typing import Dict, Generator, List
from urllib.parse import urlparse

import streamlit as st
import streamlit.components.v1 as components

from memory import (
    init_memory,
    sync_memory_from_messages,
    clear_memory,
)

INFOSYS_SRC = Path(__file__).resolve().parent / "infosys" / "src"
if INFOSYS_SRC.exists() and str(INFOSYS_SRC) not in sys.path:
    sys.path.insert(0, str(INFOSYS_SRC))

IMPORT_ERROR = ""
try:
    infosys_main = import_module("opendeepresearcher.main")
    infosys_ask = getattr(infosys_main, "ask", None)
    infosys_run = getattr(infosys_main, "run", None)
    infosys_config = import_module("opendeepresearcher.config")
    infosys_get_settings = getattr(infosys_config, "get_settings", None)
except Exception as exc:  # pragma: no cover - runtime environment dependent
    infosys_ask = None
    infosys_run = None
    infosys_get_settings = None
    IMPORT_ERROR = str(exc)


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hi! I am your project assistant. Ask me anything about your app.",
                "generated": False,
            }
        ]
    if "backend_mode" not in st.session_state:
        st.session_state.backend_mode = "Quick Answer"
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "Light"
    if "backend_reachability_cache" not in st.session_state:
        st.session_state.backend_reachability_cache = {}
    init_memory()
    sync_memory_from_messages(st.session_state.messages)


def format_deep_research_result(result: Dict[str, object], topic: str) -> str:
    draft = str(result.get("draft", "")).strip()
    subquestions = result.get("subquestions", [])
    evidence = result.get("evidence", [])

    lines: List[str] = []
    lines.append("## Deep Research Result")
    lines.append(f"**Topic:** {result.get('topic', topic)}")
    lines.append("")

    lines.append("### Summary")
    lines.append(draft if draft else "No summary draft returned from backend.")
    lines.append("")

    lines.append("### Planned Sub-Questions")
    if isinstance(subquestions, list) and subquestions:
        for question in subquestions[:8]:
            lines.append(f"- {question}")
    else:
        lines.append("- No sub-questions returned.")
    lines.append("")

    lines.append("### Evidence Highlights")
    if isinstance(evidence, list) and evidence:
        for item in evidence[:5]:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "Untitled source")).strip() or "Untitled source"
            url = str(item.get("url", "")).strip()
            snippet = str(item.get("content", "")).strip()
            if len(snippet) > 220:
                snippet = snippet[:220].rstrip() + "..."

            if url:
                lines.append(f"- [{title}]({url})")
            else:
                lines.append(f"- {title}")

            if snippet:
                lines.append(f"  {snippet}")
    else:
        lines.append("- No evidence returned.")

    return "\n".join(lines)


def is_backend_endpoint_reachable(base_url: str, timeout_seconds: float = 2.0) -> bool:
    parsed = urlparse(base_url)
    host = parsed.hostname
    port = parsed.port
    if not host:
        return False

    if port is None:
        if parsed.scheme == "https":
            port = 443
        else:
            port = 80

    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            return True
    except OSError:
        return False


def is_backend_endpoint_reachable_cached(
    base_url: str,
    timeout_seconds: float = 0.4,
    ttl_seconds: float = 20.0,
) -> bool:
    now = time.time()
    cache = st.session_state.backend_reachability_cache
    cached = cache.get(base_url)
    if cached:
        is_reachable = bool(cached.get("reachable", False))
        checked_at = float(cached.get("checked_at", 0.0))
        if now - checked_at <= ttl_seconds:
            return is_reachable

    reachable = is_backend_endpoint_reachable(base_url, timeout_seconds=timeout_seconds)
    cache[base_url] = {"reachable": reachable, "checked_at": now}
    return reachable


def build_assistant_reply(user_text: str, history: List[Dict[str, str]], mode: str) -> str:
    user_text = user_text.strip()
    if not user_text:
        return "I did not receive any message."

    if infosys_ask is None or infosys_run is None:
        return (
            "infosys backend is not importable yet.\n\n"
            "Fix steps:\n"
            "1. Install backend dependencies: `pip install -r infosys/requirements.txt`\n"
            "2. Install backend package: `pip install -e ./infosys`\n"
            f"3. Import error: `{IMPORT_ERROR}`"
        )

    if infosys_get_settings is not None:
        settings = infosys_get_settings()
        provider = getattr(settings, "llm_provider", "")
        base_url = getattr(settings, "llm_base_url", "")
        stub_on_error = bool(getattr(settings, "llm_stub_on_error", False))
        if provider in {"lmstudio", "openai_compatible", "ollama"} and base_url:
            if not is_backend_endpoint_reachable_cached(base_url) and not stub_on_error:
                return (
                    "LLM backend appears offline, so no answer can be generated right now.\n\n"
                    f"Current provider: {provider}\n"
                    f"Base URL: {base_url}\n"
                    "Fix options:\n"
                    "1. Start your local model server (LM Studio/Ollama).\n"
                    "2. Or set `LLM_STUB_ON_ERROR=true` in infosys/.env for fallback replies."
                )

    try:
        if mode == "Deep Research":
            result = infosys_run(user_text)
            if isinstance(result, dict):
                return format_deep_research_result(result, user_text)
            return f"Unexpected Deep Research payload: `{type(result).__name__}`"

        answer = infosys_ask(user_text)
        text = "" if answer is None else str(answer).strip()
        if not text:
            return (
                "Backend returned an empty response.\n\n"
                "Quick checks:\n"
                "1. Verify LLM model name is valid for your provider.\n"
                "2. If using LM Studio, ensure the model is loaded and server is started.\n"
                "3. Set `LLM_STUB_ON_ERROR=true` in infosys/.env for fallback replies."
            )
        return text
    except Exception as exc:
        return f"Backend call failed: `{exc}`"


def stream_text(text: str, delay: float = 0.015) -> Generator[str, None, None]:
    rendered = ""
    for ch in text:
        rendered += ch
        yield rendered
        time.sleep(delay)


def render_header() -> None:
    st.set_page_config(
        page_title="Project Chat",
        page_icon="💬",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    theme_mode = st.session_state.get("theme_mode", "Light")
    if theme_mode == "Dark":
        css_vars = """
            --app-bg: #0e1117;
            --panel-bg: #161b22;
            --text-color: #e6edf3;
            --muted-color: #9da7b3;
            --border-color: rgba(157, 167, 179, 0.25);
            --input-bg: #0d1117;
            --input-border: #30363d;
        """
    else:
        css_vars = """
            --app-bg: #f8fafc;
            --panel-bg: #ffffff;
            --text-color: #111827;
            --muted-color: #667085;
            --border-color: rgba(17, 24, 39, 0.12);
            --input-bg: #ffffff;
            --input-border: #d1d5db;
        """

    st.markdown(
        f"""
        <style>
            :root {{
                {css_vars}
            }}
            * {{
                color: var(--text-color) !important;
            }}
            [data-testid="stAppViewContainer"] {{
                background: var(--app-bg) !important;
            }}
            [data-testid="stHeader"] {{
                background: var(--app-bg) !important;
            }}
            [data-testid="stSidebar"] {{
                background: var(--panel-bg) !important;
                border-right: 1px solid var(--border-color);
            }}
            .block-container {{
                max-width: 860px;
                padding-top: 2.2rem;
                padding-bottom: 2rem;
            }}
            .stChatMessage {{
                border-radius: 14px;
                padding: 0.3rem 0.6rem;
                border: 1px solid var(--border-color);
                background: var(--panel-bg) !important;
            }}
            .stTextInput > div > div > input,
            .stSelectbox > div > div > select,
            .stRadio > div > label > div,
            .stTextArea textarea,
            [data-testid="stMarkdownContainer"] p,
            [data-testid="stMarkdownContainer"] span {{
                color: var(--text-color) !important;
            }}
            select, input {{
                background-color: var(--input-bg) !important;
                color: var(--text-color) !important;
                border: 1px solid var(--input-border) !important;
            }}
            select option {{
                background-color: var(--input-bg) !important;
                color: var(--text-color) !important;
            }}
            [data-baseweb="select"] {{
                background-color: var(--input-bg) !important;
            }}
            [data-baseweb="select"] span {{
                color: var(--text-color) !important;
            }}
            [data-baseweb="select"] input {{
                background-color: var(--input-bg) !important;
                color: var(--text-color) !important;
            }}
            .stSelectbox label {{
                color: var(--text-color) !important;
            }}
            .stSelectbox > div > div {{
                background-color: var(--input-bg) !important;
                color: var(--text-color) !important;
            }}
            .stSelectbox > div > div > div {{
                background-color: var(--input-bg) !important;
                color: var(--text-color) !important;
            }}
            .stSelectbox input {{
                background-color: var(--input-bg) !important;
                color: var(--text-color) !important;
            }}
            [data-baseweb="popover"] {{
                background-color: var(--input-bg) !important;
            }}
            [data-baseweb="popover"] > div {{
                background-color: var(--input-bg) !important;
                color: var(--text-color) !important;
            }}
            [data-baseweb="popover"] [role="option"] {{
                color: var(--text-color) !important;
                background-color: var(--input-bg) !important;
            }}
            [role="option"] {{
                color: var(--text-color) !important;
                background-color: var(--input-bg) !important;
            }}
            [role="option"]:hover {{
                background-color: var(--border-color) !important;
                color: var(--text-color) !important;
            }}
            button, [data-testid="stButton"] {{
                color: var(--text-color) !important;
                background-color: var(--panel-bg) !important;
            }}
            [role="tab"] {{
                color: var(--text-color) !important;
                background: transparent !important;
            }}
            [role="tabpanel"] {{
                background: var(--panel-bg) !important;
                color: var(--text-color) !important;
            }}
            .stTabs [data-baseweb="tab-bar"] {{
                background: transparent !important;
            }}
            .stTabs [role="tab"] {{
                color: var(--text-color) !important;
            }}
            label {{
                color: var(--text-color) !important;
            }}
            .chat-title {{
                font-size: 1.45rem;
                font-weight: 700;
                margin-bottom: 0;
                color: var(--text-color) !important;
            }}
            .chat-subtitle {{
                color: var(--muted-color) !important;
                margin-bottom: 0;
            }}
            .chat-hero {{
                display: flex;
                flex-direction: column;
                gap: 0.25rem;
                margin-bottom: 0.8rem;
            }}
            .chat-hero-divider {{
                height: 1px;
                width: 100%;
                margin-top: 0.55rem;
                background: var(--border-color);
            }}
            @media (max-width: 900px) {{
                .block-container {{
                    padding-top: 5rem !important;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        (
            '<div class="chat-hero">'
            '<div class="chat-title">Project Assistant</div>'
            '<div class="chat-subtitle">ChatGPT-style UI in Streamlit. Replace the response function with your own backend.</div>'
            '<div class="chat-hero-divider"></div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.subheader("Session")
        st.selectbox(
            "infosys mode",
            ["Quick Answer", "Deep Research"],
            key="backend_mode",
            help="Quick Answer uses ask(); Deep Research uses run() for a full research flow.",
        )
        st.radio(
            "Theme",
            ["Light", "Dark"],
            key="theme_mode",
            horizontal=True,
        )

        _handle_new_chat_action()
        _render_memory_sidebar_section()
        _render_backend_status()


def _handle_new_chat_action() -> None:
    if st.button("New chat", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "New chat started. What would you like to build today?",
                "generated": False,
            }
        ]
        clear_memory()
        st.rerun()


def _render_memory_sidebar_section() -> None:
    st.divider()
    st.subheader("📚 Previous Questions")

    if not st.session_state.qa_history:
        st.caption("No questions yet. Start chatting!")
        return

    for i, qa in enumerate(st.session_state.qa_history, 1):
        st.caption(f"{i}. {qa['question']}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 View All", use_container_width=True):
            st.session_state.show_memory_details = not st.session_state.get("show_memory_details", False)
            st.rerun()
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            clear_memory()
            st.rerun()

    if not st.session_state.get("show_memory_details", False):
        return

    st.divider()
    for i, qa in enumerate(st.session_state.qa_history, 1):
        with st.expander(f"Q{i}: {qa['question'][:50]}..."):
            st.markdown(f"**Q:** {qa['question']}")
            st.markdown(f"**A:** {qa['answer']}")


def _render_backend_status() -> None:
    st.divider()
    if infosys_ask is None or infosys_run is None:
        st.warning("infosys backend not loaded")
    else:
        st.success("infosys backend connected")
        if infosys_get_settings is not None:
            try:
                settings = infosys_get_settings()
                st.caption(
                    f"Provider: {getattr(settings, 'llm_provider', 'unknown')} | "
                    f"Model: {getattr(settings, 'llm_model', 'unknown')}"
                )
            except Exception:
                st.caption("Provider/Model: unavailable")

    st.caption("This UI is linked to infosys/src/opendeepresearcher via runtime import path setup.")


def _render_response_actions(response_text: str, key_suffix: str) -> None:
    col_copy, col_share = st.columns(2)

    with col_copy:
        safe_text = json.dumps(response_text)
        components.html(
            f"""
            <button id=\"copy-btn-{key_suffix}\" style=\"
                width: 100%;
                padding: 0.38rem 0.7rem;
                border-radius: 0.5rem;
                border: 1px solid #9aa0a6;
                background: #f6f8fa;
                color: #111827;
                font-weight: 600;
                cursor: pointer;
            \">Copy</button>
            <script>
                const copyBtn = document.getElementById("copy-btn-{key_suffix}");
                copyBtn.addEventListener("click", async () => {{
                    try {{
                        await navigator.clipboard.writeText({safe_text});
                        copyBtn.textContent = "Copied";
                    }} catch (err) {{
                        copyBtn.textContent = "Copy failed";
                    }}
                    setTimeout(() => {{ copyBtn.textContent = "Copy"; }}, 1200);
                }});
            </script>
            """,
            height=42,
        )

    with col_share:
        st.download_button(
            "Share",
            data=response_text,
            file_name=f"assistant-answer-{key_suffix}.txt",
            mime="text/plain",
            key=f"share_{key_suffix}",
            use_container_width=True,
        )


def _render_messages() -> None:
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and bool(message.get("generated", False)):
                _render_response_actions(str(message.get("content", "")), f"history_{idx}")


def _append_user_message(prompt: str) -> None:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


def _generate_reply(prompt: str, mode: str) -> str:
    reply = build_assistant_reply(prompt, st.session_state.messages, mode)

    if reply is None:
        return "Backend returned no content."
    return str(reply)


def _render_assistant_reply(reply: str) -> None:
    with st.chat_message("assistant"):
        placeholder = st.empty()
        for partial in stream_text(reply):
            placeholder.markdown(partial)
        _render_response_actions(reply, f"live_{len(st.session_state.messages)}")


def _handle_prompt_submission(prompt: str) -> None:
    _append_user_message(prompt)

    with st.spinner("Thinking..."):
        reply = _generate_reply(prompt, st.session_state.backend_mode)

    _render_assistant_reply(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply, "generated": True})
    sync_memory_from_messages(st.session_state.messages)


def main() -> None:
    render_header()
    init_state()
    sync_memory_from_messages(st.session_state.messages)
    render_sidebar()

    _render_messages()

    prompt = st.chat_input("Message your assistant...")
    if not prompt:
        return

    _handle_prompt_submission(prompt)


if __name__ == "__main__":
    main()
