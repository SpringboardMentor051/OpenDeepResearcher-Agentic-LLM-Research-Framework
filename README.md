OpenDeepResearcher: Agentic LLM Research Framework

Description
OpenDeepResearcher is an AI-powered research assistant capable of autonomously conducting in-depth explorations of complex topics. It leverages large language models (LLMs), agentic workflows, and web search APIs to streamline the research process by automatically planning, retrieving, analyzing, and summarizing information from credible sources.

By simulating the behavior of a skilled human researcher, the tool enables users to generate high-quality, multi-perspective reports efficiently and cost-effectively.


Tech Stack

-Language: Python 3.10+
-Agentic Framework: LangGraph, LangChain
-LLM Integration: LM Studio / Ollama / API (e.g., Qwen2.5-7B-Instruct)
-LLM Integration: LM Studio (Qwen2.5-3B-Instruct) 
  Note: Originally planned with Qwen2.5-7B-Instruct, switched to 3B due to hardware limitations.
-Web Search:Tavily: API
-Memory Management: MemorySaver
-Environment Tools: pip, venv, Git


Project Workflow

1.Planning — A Planner Agent breaks the prompt into sub-questions and creates a research roadmap.
2.Information Retrieval — A Searcher Agent queries the web via Tavily to collect relevant content.
3.Synthesis — A Writer Agent analyzes and summarizes the retrieved data using an LLM.
4.Report Generation — The system compiles all findings into a structured research report.
5.Session Memory (Optional) — Research threads are stored for continuity and future reference.


Architecture


Topic → [Planner Agent] → [Searcher Agent / Web Search] → [Writer Agent] → Final Report with Sources
                                    

Components

-Planner Agent — Breaks down the main query into sub-questions and creates a research plan.
-Searcher Agent — Uses Tavily API to retrieve relevant, up-to-date content from the web.
-Writer Agent — Synthesizes retrieved data into structured, coherent summaries using an LLM.
-Memory System — Stores session data to support iterative and multi-step research.
-Execution Graph — Manages the flow between agents using LangGraph.
-Model Interface — Allows integration with local or hosted LLMs via LM Studio.


Project Milestones

| Milestone | Weeks |                               Focus                           |

| 1         | 1–2   | Foundation Setup – environment, architecture, LLM integration |
| 2         | 3–4   | Core Agent Development – Planner, Searcher, Writer agents     |
| 3         | 5–6   | UI and Memory Integration – ChatGPT-like UI, session memory   |
| 4         | 7–8   | Refinement and Final Output – optimization, citations, demo   |


Installation & Setup (Milestone 1 Completed)

1.Created a Python Virtual Environment:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

2.Installed Dependencies:

pip install langchain langgraph openai


3.Set up LM Studio:
-Downloaded and installed LM Studio
-Downloaded the Qwen2.5-3B-Instruct model inside LM Studio
-LLM Integration: LM Studio (Qwen2.5-3B-Instruct) 
  Note: Originally planned with Qwen2.5-7B-Instruct, switched to 3B due to hardware limitations.
-Started the local server in LM Studio (runs on http://localhost:1234)

4.Integrated LM Studio with the Project
-LM Studio provides an OpenAI-compatible API
-Set the base URL to http://localhost:1234/v1 in the code
-No API key required for local usage

How to Run
In terminal enter:
python main.py

Author
ULLI NAGA SRI VENKATA NAVYA SRI 
Intern