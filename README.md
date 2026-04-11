# 🔍 AI Research Assistant (Multi-Agent System)

A fully automated **AI-powered Research Assistant** built using:
**LangGraph + LangChain + Ollama + Tavily API + Streamlit**

It performs end-to-end research by breaking a topic into sub-questions, searching the web, and generating structured academic reports.

---

# 🚀 Features

- 🧠 AI Planner Agent → Generates research sub-questions  
- 🔎 Search Agent → Fetches real-time web data using Tavily API  
- ✍️ Writer Agent → Generates structured research reports using LLM  
- 🔗 LangGraph workflow → Multi-agent orchestration  
- 📜 History system (saved locally in JSON)  

---

## 🏗️ System Architecture

```text
User Input → Planner Agent → Searcher Agent → Writer Agent → Final Report
```


## 📂 Project Structure

```
OpenDeepResearcher-Agentic-LLM-Research-Framework/
│
├── ui.py                  # Streamlit frontend UI
├── main.py                # LangGraph workflow controller
│
├── agents/
│   ├── planner.py        # Generates research questions
│   ├── searcher.py       # Web search using Tavily API
│   ├── writer.py         # LLM report generator
│
├── history.json          # Stores user search history
├── requirements.txt      # Python dependencies
├── .env                  # API keys (not pushed to GitHub)
├── .gitignore
└── README.md
```



---

# ⚙️ Installation & Setup

## 1️⃣ Clone Repository


git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

## 2️⃣ Create Virtual Environment (Recommended)

  python -m venv venv

## 3️⃣ Install Dependencies

pip install -r requirements.txt


##4️⃣ Setup Environment Variables

Create a .env file in root folder:

TAVILY_API_KEY=your_tavily_api_key_here


## 5️⃣ Install Ollama (Local LLM)
 ollama run gemma:2b

## ▶️ Run the Project
streamlit run ui.py
