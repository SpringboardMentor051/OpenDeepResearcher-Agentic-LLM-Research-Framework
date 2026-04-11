# OpenDeepResearcher

## 📌 Description

OpenDeepResearcher is a multi-agent AI research system that generates structured, source-backed reports using a ChatGPT-like conversational interface.
It integrates planning, web search, and report generation into a seamless research workflow.

---

## 🚀 Features

### 🤖 Multi-Agent Pipeline

* **Planner Agent** – Breaks user query into sub-questions
* **Search Agent (Tavily)** – Retrieves relevant web sources
* **Writer Agent** – Generates structured research reports

### 💬 ChatGPT-like UI

* Clean conversational interface (Streamlit)
* Multi-chat support
* Chat switching and history

### 🧠 Memory System

* Persistent chat storage (JSON-based)
* Session continuity across restarts

### 📄 Report Generation

* Structured outputs (Title, Sections, Conclusion)
* Source references included
* Export reports as **PDF**

### ⚡ Performance Optimization

* Limited context memory
* Optimized search queries
* Faster response generation

---

## 📂 Project Structure

```
milestone2/
  ├── agents/
  ├── graph/
  ├── utils/

milestone3/
  ├── ui/
  ├── backend/
  ├── memory/
```

---

## 🛠️ Technologies Used

* Python
* Streamlit
* LangChain
* Tavily API
* ReportLab

---

## ▶️ How to Run

```bash
# Activate virtual environment
venv\Scripts\activate

# Run the application
streamlit run milestone3/ui/app.py
```

---

## 📊 Milestones Completed

* **Milestone 2**: Multi-agent research pipeline
* **Milestone 3**: UI + Memory integration
* **Milestone 4**: Performance optimization + PDF export

---

## 🎯 Key Highlights

* ChatGPT-like experience for research
* Multi-agent architecture
* Persistent memory system
* Professional PDF report generation

---

## 📌 Future Improvements

* Streaming responses
* Dark mode UI
* AI-generated chat titles
* Advanced citation formatting

---

## 👨‍💻 Author

Dedeepya
