 🧠 OpenDeepResearcher

> **An Agentic LLM Research Framework** — Autonomously plan, search, synthesize, and report on any research topic using a multi-agent pipeline.
---

 📖 Overview

**OpenDeepResearcher** is an AI-powered research assistant that takes any query, breaks it into focused sub-questions, searches the web in parallel, and synthesizes everything into a structured, professional report — with PDF export built in.

It handles both fresh queries and follow-up questions intelligently, using conversation history to avoid repeating prior context and go deeper on new aspects.

---

 🏗️ Architecture

The system runs as a **LangGraph pipeline** with four sequential nodes:

```
User Query
    └──▶ [1] Follow-Up Detector   — Is this a follow-up to prior conversation?
              └──▶ [2] Planner Agent     — Breaks query into 4 focused sub-questions
                        └──▶ [3] Parallel Research  — Search + Write for each sub-question (4 threads)
                                  └──▶ [4] Final Writer    — Synthesizes all partials into a full report
                                                └──▶ Structured Report (+ PDF export)
```

---

 📁 Project Structure

```
OpenDeepResearcher/
├── main.py                   Entry point — builds graph and runs research
├── app.py                    Streamlit UI with multi-chat sidebar
├── utils/
│   └── pdf_export.py         Markdown → styled PDF via ReportLab
├── graph/
│   └── pipeline.py           LangGraph pipeline (4 nodes + state definition)
└── agents/
    ├── planner.py             Planner Agent — generates 4 sub-questions
    ├── searcher.py            Searcher Agent — Tavily web search + formatting
    └── writer.py              Writer Agent — partial and final report synthesis
```

---

 🔄 How It Works

 1. Follow-Up Detection (`pipeline.py`)
Before planning, the pipeline checks if the new query is a follow-up to prior conversation. It sends recent chat history + the new query to the LLM and gets a YES/NO answer. This determines how the Planner and Writer behave downstream.

 2. Planner Agent (`agents/planner.py`)
Takes the user query (and conversation history if follow-up) and generates exactly **4 focused sub-questions** via the LLM. For follow-ups, it generates questions about the *new* aspect only — avoiding anything already covered. Includes 4-layer fallback parsing (direct JSON → regex → line splitting → hardcoded defaults).

 3. Parallel Search + Write (`pipeline.py` → `agents/searcher.py` + `agents/writer.py`)
Each of the 4 sub-questions is processed **concurrently** using `ThreadPoolExecutor(max_workers=4)`:
- **Searcher** queries Tavily with `search_depth="advanced"`, up to 5 results, with a fallback to `"basic"` if no results are returned.
- **Writer** synthesizes the search results for that sub-question into a focused paragraph-based partial summary.

 4. Final Writer (`agents/writer.py`)
Combines all 4 partial summaries and writes the final structured report. Uses a different prompt for follow-up vs. fresh queries — follow-ups skip generic introductions and focus only on the new aspect.

 5. Streamlit UI (`app.py`)
- Multi-chat sidebar (create, switch, delete chats)
- Live status updates during research (detecting → planning → searching → writing)
- Expandable "Research Process" toggle showing sub-questions explored
- **PDF download** for every report via ReportLab

 6. PDF Export (`utils/pdf_export.py`)
Converts the markdown report to a styled PDF using ReportLab — handles headings (H1/H2/H3), bullet points, bold/italic/code inline formatting, horizontal rules, and source URL styling.

---

 🛠️ Tech Stack

| Component | Technology |
___________________________
| Language | Python 3.10+ |
| Agent Pipeline | LangGraph |
| LLM Interface | OpenAI-compatible API (LM Studio / Ollama / any endpoint) |
| Web Search | Tavily API |
| UI | Streamlit |
| PDF Export | ReportLab |
| Concurrency | `concurrent.futures.ThreadPoolExecutor` |
| Config | `python-dotenv` |

---

 🚀 Getting Started

 Prerequisites

- Python 3.10+
- [Tavily API Key](https://tavily.com/)
- An OpenAI-compatible LLM endpoint (LM Studio, Ollama, or any hosted model)

 Installation

```bash
git clone https://github.com/your-username/OpenDeepResearcher.git
cd OpenDeepResearcher

python -m venv venv
source venv/bin/activate         Windows: venv\Scripts\activate

pip install -r requirements.txt
```

 Configuration

Create a `.env` file in the project root:

```env
TAVILY_API_KEY=your_tavily_api_key_here
API_KEY=your_llm_api_key_here
BASE_URL=http://localhost:1234/v1
MODEL_NAME=qwen2.5-7b-instruct
```

 Run

```bash
streamlit run app.py
```

---

 📦 Dependencies

```txt
langchain
langgraph
openai
tavily-python
streamlit
reportlab
python-dotenv
```

---

 👤 Author
Built by Mahesh Reddy, as part of Springboard virtual internship 6.0, 2026.

---

 📄 License

MIT License. See [LICENSE](LICENSE) for details.
