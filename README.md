# OpenDeepResearcher

## Overview

This project is an AI-based research assistant that helps users explore topics automatically using a multi-agent system.

---

## How it Works

1. User enters a topic
2. Planner Agent generates questions
3. Searcher Agent collects data from the web
4. Writer Agent creates a research report

---

## Features

* Multi-agent system (Planner, Searcher, Writer)
* Real-time web search using Tavily API
* Report generation using LLM
* Streamlit-based chat interface
* Chat history (memory)
* PDF download

---

## Tech Stack

* Python
* Streamlit
* LM Studio (Qwen model)
* Tavily API

---

## How to Run

1. Install dependencies:
   pip install -r requirements.txt

2. Add API key in `.env`:
   TAVILY_API_KEY=your_key

3. Run:
   streamlit run app.py

---

## My Work

* Built Planner, Searcher, Writer agents
* Connected them using a pipeline
* Integrated LLM and Tavily API
* Created Streamlit UI

---

## License

MIT License
