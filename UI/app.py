import sys
import os
sys.path.append(os.path.abspath(".."))

import streamlit as st
from main import run_research
from utils.pdf_export import markdown_to_pdf_bytes

# ──────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────
st.set_page_config(
    page_title="OpenDeepResearcher",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 OpenDeepResearcher")
st.caption("Ask any research question — I'll plan, search, and synthesize a full report.")

# ──────────────────────────────────────────
# SESSION INIT
# ──────────────────────────────────────────
if "conversations" not in st.session_state:
    st.session_state.conversations = {"Chat 1": []}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

# Ensure current chat exists
if st.session_state.current_chat not in st.session_state.conversations:
    st.session_state.conversations[st.session_state.current_chat] = []

# ──────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────
with st.sidebar:
    st.title("💬 Chats")

    if st.button("➕ New Chat", use_container_width=True):
        new_chat_id = f"Chat {len(st.session_state.conversations) + 1}"
        st.session_state.conversations[new_chat_id] = []
        st.session_state.current_chat = new_chat_id
        st.rerun()

    st.divider()

    for chat_name in list(st.session_state.conversations.keys()):
        is_active = chat_name == st.session_state.current_chat
        label = f"**{chat_name}**" if is_active else chat_name
        if st.button(label, key=f"nav_{chat_name}", use_container_width=True):
            st.session_state.current_chat = chat_name
            st.rerun()

    st.divider()

    if st.button("🗑️ Delete Current Chat", use_container_width=True):
        if len(st.session_state.conversations) > 1:
            del st.session_state.conversations[st.session_state.current_chat]
            st.session_state.current_chat = list(st.session_state.conversations.keys())[0]
            st.rerun()
        else:
            st.warning("Cannot delete the only chat.")

    st.divider()
    st.caption("Built with LangGraph + Tavily + OpenAI")

# ──────────────────────────────────────────
# CHAT DISPLAY
# ──────────────────────────────────────────
messages = st.session_state.conversations[st.session_state.current_chat]

for i, msg in enumerate(messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Assistant extras: research steps + PDF download
        if msg["role"] == "assistant":
            col1, col2 = st.columns([1, 1])

            # 🔍 Research process toggle
            with col1:
                steps = msg.get("steps", {})
                if steps.get("planning"):
                    if st.button("🔍 Research Process", key=f"steps_{i}"):
                        msg["expanded"] = not msg.get("expanded", False)

                    if msg.get("expanded", False):
                        with st.expander("📋 Research Plan & Partial Summaries", expanded=True):
                            st.markdown("**Sub-questions explored:**")
                            for q in steps.get("planning", []):
                                st.write(f"• {q}")

            # 📄 PDF download button
            with col2:
                if msg["content"] and not msg["content"].startswith("❌"):
                    try:
                        pdf_bytes = markdown_to_pdf_bytes(
                            msg["content"],
                            title="Research Report"
                        )
                        st.download_button(
                            label="📄 Download PDF",
                            data=pdf_bytes,
                            file_name=f"research_report_{i}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{i}"
                        )
                    except Exception as e:
                        st.caption(f"PDF unavailable: {e}")

# ──────────────────────────────────────────
# CHAT INPUT
# ──────────────────────────────────────────
user_input = st.chat_input("Ask a deep research question...")

if user_input and user_input.strip():
    # Append user message
    messages.append({"role": "user", "content": user_input.strip()})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Run research
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        content_placeholder = st.empty()

        # Build history (last 10 messages for context)
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
            if m["role"] in ("user", "assistant")
        ][-10:]

        # Step-by-step status updates
        with status_placeholder.status("🧠 Researching...", expanded=False) as status:
            st.write("🔍 Detecting follow-up context...")
            st.write("📋 Planning research questions...")
            st.write("🌐 Searching the web in parallel...")
            st.write("✍️ Synthesizing final report...")

            try:
                result = run_research(user_input.strip(), history)
                final_answer = result["final_answer"]
                steps = result.get("steps", {})
                is_followup = result.get("is_followup", False)
                status.update(label="✅ Research complete!", state="complete", expanded=False)
            except Exception as e:
                final_answer = f"❌ Unexpected error: {str(e)}"
                steps = {}
                is_followup = False
                status.update(label="❌ Error occurred", state="error", expanded=True)

        status_placeholder.empty()

        # Display final answer
        content_placeholder.markdown(final_answer)

        # Follow-up badge
        if is_followup:
            st.caption("🔗 *Follow-up response — built on prior conversation*")

        # PDF download for new response
        if final_answer and not final_answer.startswith("❌"):
            try:
                pdf_bytes = markdown_to_pdf_bytes(final_answer, title="Research Report")
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_bytes,
                    file_name="research_report.pdf",
                    mime="application/pdf",
                    key=f"pdf_new_{len(messages)}"
                )
            except Exception as e:
                st.caption(f"PDF generation failed: {e}")

    # Save assistant message
    messages.append({
        "role": "assistant",
        "content": final_answer,
        "steps": steps,
        "expanded": False
    })
