# 🧠 OpenDeepResearcher: Agentic LLM Research Framework

An AI-powered research assistant that autonomously explores complex topics using multi-agent workflows, large language models (LLMs), and real-time web search.

---

## 🚀 Overview

OpenDeepResearcher simulates the behavior of a human researcher by:

* Breaking down complex queries into smaller research tasks
* Retrieving relevant information from the web
* Synthesizing insights into structured summaries
* Maintaining conversation context across sessions

The system is designed to generate **high-quality, multi-perspective research reports efficiently**.

---

## 🧩 Architecture

The system follows a multi-agent pipeline:

```
User Query
   ↓
🧠 Planner Agent → Generates research questions
   ↓
🌐 Searcher Agent → Fetches web data (Tavily API)
   ↓
✍️ Writer Agent → Summarizes using LLM
   ↓
📄 Final Structured Research Output
```

---

## 🤖 Core Components

### 🧠 Planner Agent

* Breaks the main topic into smaller search queries
* Guides the research workflow

### 🌐 Searcher Agent

* Uses Tavily API to fetch relevant web results
* Collects real-time information

### ✍️ Writer Agent

* Synthesizes data into structured summaries
* Uses LLM (LM Studio / OpenAI-compatible)

### 💾 Memory System

* Stores conversation history
* Enables multi-step research continuity

### 🖥️ Streamlit UI

* ChatGPT-like interface
* Suggestion prompts
* Centered input box
* Clean and interactive design

---

## 🛠️ Tech Stack

* **Python 3.10+**
* **Streamlit** – UI
* **LangChain** – LLM integration
* **Tavily API** – Web search
* **LM Studio / OpenAI API** – LLM backend
* **Git & GitHub** – Version control

---

## 📁 Project Structure

```
OpenDeepResearcher/
│
├── agents/
│   ├── planner.py
│   ├── searcher.py
│   ├── writer.py
│
├── memory/
│   ├── __init__.py
│
├── data/
│   ├── chats.json
│
├── app.py              # Streamlit UI
├── main.py             # Backend runner
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd OpenDeepResearcher
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add Environment Variables

Create a `.env` file:

```
TAVILY_API_KEY=your_api_key_here
LM_STUDIO_BASE_URL=http://127.0.0.1:1234
LM_STUDIO_MODEL=qwen2.5-7b-instruct
```

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

Then open:

```
http://localhost:8501
```

---

## ✨ Features

* ✅ Multi-agent research pipeline
* ✅ Real-time web search integration
* ✅ Structured research summaries
* ✅ Chat-based UI
* ✅ Session memory support
* ✅ Modular and extensible design

---

## 📌 Example Use Cases

* Academic research assistance
* Technical topic exploration
* Market research
* Learning complex concepts

---

## ⚠️ Known Limitations

* LangGraph integration (planned improvement)
* Output formatting can be further enhanced
* Memory system can be extended for long-term persistence

---

## 🔮 Future Improvements

* 🔁 Add LangGraph workflow orchestration
* 📊 Better structured report formatting
* 🧠 Enhanced memory handling
* 🌍 Multi-source validation and ranking

---

## 👨‍💻 Author

**Seshank**

---

## ⭐ Contributing

Contributions are welcome! Feel free to fork the repo and submit a pull request.

---

## 📜 License

This project is for educational and research purposes.
