# Milestone 3: UI and Memory Integration

## Features Implemented

- ChatGPT-like UI using Streamlit
- User input and response display
- Integration with backend agent pipeline
- Session memory using Streamlit session_state
- Multi-chat support (thread tracking)
- Context-aware responses using previous messages
- Persistent chat storage using JSON file

## Architecture

User → Streamlit UI → Pipeline Wrapper → Planner → Searcher → Writer → Response

## Memory Implementation

- Session memory: stores conversation during runtime
- Persistent memory: stores chats in JSON file
- Context passing: last messages sent to LLM for continuity

## How to Run

```bash
streamlit run milestone3/ui/app.py