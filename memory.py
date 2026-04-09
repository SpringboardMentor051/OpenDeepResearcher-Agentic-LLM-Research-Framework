"""Short-term memory management using Streamlit session state."""

import time
from typing import Dict, List

import streamlit as st


def init_memory() -> None:
    """Initialize memory state in session."""
    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []
    if "memory_size" not in st.session_state:
        st.session_state.memory_size = 5  # Store last 5 Q&A pairs


def add_to_memory(question: str, answer: str) -> None:
    """Add a question-answer pair to short-term memory.
    
    Args:
        question: User's question
        answer: Assistant's answer
    """
    qa_pair = {
        "question": question.strip(),
        "answer": answer.strip(),
        "timestamp": time.time(),
    }
    st.session_state.qa_history.append(qa_pair)
    # Keep only the last N pairs
    if len(st.session_state.qa_history) > st.session_state.memory_size:
        st.session_state.qa_history = st.session_state.qa_history[-st.session_state.memory_size :]


def sync_memory_from_messages(messages: List[Dict[str, str]]) -> None:
    """Rebuild memory from chat messages to keep state consistent across reruns."""
    qa_history: List[Dict[str, object]] = []
    pending_question = ""

    for msg in messages:
        role = str(msg.get("role", "")).strip().lower()
        content = str(msg.get("content", "")).strip()
        if not content:
            continue

        if role == "user":
            pending_question = content
            continue

        if role == "assistant" and pending_question:
            qa_history.append(
                {
                    "question": pending_question,
                    "answer": content,
                    "timestamp": time.time(),
                }
            )
            pending_question = ""

    if len(qa_history) > st.session_state.memory_size:
        qa_history = qa_history[-st.session_state.memory_size :]

    st.session_state.qa_history = qa_history


def get_memory_context() -> str:
    """Format recent Q&A history as context string for the LLM.
    
    Returns:
        Formatted context string or empty string if no history
    """
    if not st.session_state.qa_history:
        return ""
    
    context_lines = ["## Recent Context"]
    for i, qa in enumerate(st.session_state.qa_history, 1):
        context_lines.append(f"Q{i}: {qa['question']}")
        context_lines.append(f"A{i}: {qa['answer']}")
    
    return "\n".join(context_lines)


def get_recent_qa_pairs(count: int = 3) -> List[Dict[str, str]]:
    """Get the last N question-answer pairs from memory.
    
    Args:
        count: Number of recent pairs to retrieve
        
    Returns:
        List of Q&A pair dictionaries
    """
    return st.session_state.qa_history[-count:] if st.session_state.qa_history else []


def clear_memory() -> None:
    """Clear all short-term memory."""
    st.session_state.qa_history = []


def get_memory_stats() -> Dict[str, int]:
    """Get statistics about current memory usage.
    
    Returns:
        Dictionary with 'pairs' and 'max_size' keys
    """
    return {
        "pairs": len(st.session_state.qa_history),
        "max_size": st.session_state.memory_size,
    }
