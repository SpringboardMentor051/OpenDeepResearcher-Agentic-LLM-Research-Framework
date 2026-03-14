OpenDeepResearcher: Agentic LLM Research Framework

Description

OpenDeepResearcher is an AI-powered research assistant designed to autonomously conduct 
in-depth explorations of complex topics. Traditional research requires hours of manually 
searching, reading, and summarizing information from multiple sources. This project solves 
that problem by building an intelligent system that does all of that automatically.

The system leverages the power of Large Language Models (LLMs), agentic workflows, and 
web search APIs to plan, retrieve, analyze, and summarize information from credible sources 
on the internet. By simulating the behavior of a skilled human researcher, OpenDeepResearcher 
enables users to generate high-quality, multi-perspective research reports efficiently and 
cost-effectively.

This project is built entirely using open-source tools and runs locally on your machine, 
making it privacy-friendly and cost-effective without relying on paid cloud APIs.


Tech Stack

- Language: Python 3.10+
  Python was chosen as the core language because of its rich ecosystem of AI and ML libraries,
  ease of use, and strong community support.

- Agentic Framework: LangGraph, LangChain
  LangGraph is used to define and manage multi-agent workflows. LangChain provides the tools
  needed for LLM integration, memory handling, and agent coordination.

- LLM Integration: LM Studio (Qwen2.5-3B-Instruct)
  LM Studio is used to run large language models locally on the machine. The Qwen2.5-3B-Instruct
  model was used for both planning and writing tasks.
  Note: The project was originally planned with Qwen2.5-7B-Instruct but was switched to the 
  3B version due to hardware limitations on the development machine. The 3B model performs 
  well for the current scope of the project.

- Web Search: Tavily API
  Tavily is a search API designed specifically for AI agents. It retrieves relevant and 
  up-to-date content from the web in a structured format that is easy for LLMs to process.

- Memory Management: MemorySaver
  MemorySaver is used to store research session data so that the system can support 
  multi-step and iterative research without losing context.

- Environment Tools: pip, venv, Git
  Standard Python tools used for dependency management, virtual environment setup, 
  and version control.


Project Workflow

The research process follows a structured pipeline where each step builds on the previous one:

1. Planning — When the user enters a research topic, the Planner Agent takes over. It 
   analyzes the topic and breaks it down into 3 focused sub-questions. This creates a 
   clear research roadmap for the system to follow.

2. Information Retrieval — The Searcher Agent takes each sub-question and searches the web 
   using the Tavily API. It collects relevant, up-to-date content from credible sources 
   on the internet.

3. Synthesis — The Writer Agent receives all the information gathered by the Searcher Agent. 
   It uses the LLM to analyze, organize, and summarize the content into a clear and 
   structured response.

4. Report Generation — All the summaries and findings are compiled together into a final 
   structured research report that is easy to read and understand.

5. Session Memory (Optional) — The system can store research threads using MemorySaver so 
   that users can continue or refer back to previous research sessions without starting over.


Architecture

The system follows a linear pipeline with a reflection loop for improved accuracy:

Topic entered by user
      ↓
Planner Agent — breaks topic into sub-questions
      ↓
Searcher Agent — retrieves information from the web
      ↓
Writer Agent — synthesizes and summarizes the findings
      ↓
Final Report with cited sources delivered to the user
      ↑
Reflection Loop — the system can loop back to improve results


Components

Planner Agent (planner.py)
The Planner Agent is the first step in the research pipeline. It receives the user's 
research topic and uses the LLM to break it down into 3 focused sub-questions. These 
sub-questions act as a research roadmap, helping the system explore the topic from 
multiple angles rather than giving a single generic answer.

Searcher Agent (searcher.py)
The Searcher Agent is responsible for finding information. It takes the research topic 
or sub-questions and queries the web to retrieve relevant, up-to-date content. In the 
current milestone, the LLM itself provides background information. In future milestones, 
this will be connected to the Tavily API for real-time web search results.

Writer Agent (writer.py)
The Writer Agent is the final step in the pipeline. It takes all the information 
gathered by the Searcher Agent and uses the LLM to write a detailed, coherent summary. 
The output is a well-structured paragraph that presents the findings in a clear and 
readable format.

Memory System
The Memory System uses MemorySaver to keep track of research sessions. This allows 
the system to remember previous research threads and support multi-step research 
without losing context between interactions.

Execution Graph
The Execution Graph is built using LangGraph and manages the flow of data between 
agents. It ensures that each agent runs in the correct order and that the output of 
one agent is properly passed to the next.

Model Interface
The Model Interface connects the system to the LLM running locally in LM Studio. 
It uses an OpenAI-compatible API so that the same code can work with different 
models without major changes.


Project Structure

project/
│
├── agent/
│   ├── planner.py       — Planner Agent logic
│   ├── searcher.py      — Searcher Agent logic
│   └── writer.py        — Writer Agent logic
│
├── main.py              — Main entry point that connects all agents
├── .env                 — Environment variables (API keys, model name)
└── README.md            — Project documentation


Prerequisites

Before setting up the project make sure you have the following:

- Python 3.10 or above installed on your system
- LM Studio downloaded and installed
- The Qwen2.5-3B-Instruct model downloaded inside LM Studio
- A stable internet connection
- Basic knowledge of running Python scripts in the terminal


Installation and Setup (Milestone 1 Completed)

1. Created a Python Virtual Environment

A virtual environment was created to keep the project dependencies separate from 
other Python projects on the system. This avoids version conflicts and keeps the 
environment clean.

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

2. Installed Dependencies

The following libraries were installed to support the agentic workflow and LLM integration:

pip install langchain langgraph openai

- langchain — for LLM integration and agent coordination
- langgraph — for building and managing multi-agent workflows
- openai — for connecting to the OpenAI-compatible API provided by LM Studio

3. Set up LM Studio

LM Studio was used to run the language model locally on the machine without 
needing any paid cloud API.

- Downloaded and installed LM Studio from https://lmstudio.ai
- Searched for and downloaded the Qwen2.5-3B-Instruct model inside LM Studio
- Started the local inference server inside LM Studio
- The server runs locally on http://localhost:1234 and provides an OpenAI-compatible API

Note: The project was originally planned to use Qwen2.5-7B-Instruct but was 
switched to the 3B version because the development machine did not have enough 
RAM and GPU memory to run the 7B model smoothly. The mentor was informed and 
approved the change.

4. Integrated LM Studio with the Project

- LM Studio exposes a local API that is fully compatible with the OpenAI API format
- The base URL was set to http://localhost:1234/v1 in the code using environment variables
- The model name was set to qwen2.5-3b-instruct
- No real API key is required since the model runs locally. The string "lm-studio" 
  is used as a placeholder API key


How to Run

Make sure LM Studio is running and the local server is started before running the project.

Then open your terminal, navigate to the project folder and enter:

python main.py

The system will ask you to enter a research topic. Once you enter it, the pipeline 
will run automatically — the Planner will break it down, the Searcher will find 
information, and the Writer will generate a summary.


Project Milestones

| Milestone | Weeks | Focus |
|-----------|-------|-------|
| 1 | 1–2 | Foundation Setup – environment, architecture, LLM integration |
| 2 | 3–4 | Core Agent Development – Planner, Searcher, Writer agents |
| 3 | 5–6 | UI and Memory Integration – ChatGPT-like UI, session memory |
| 4 | 7–8 | Refinement and Final Output – optimization, citations, demo |


Challenges Faced

- The Qwen2.5-7B-Instruct model could not run on the development machine due to hardware 
  limitations. This was resolved by switching to the lighter Qwen2.5-3B-Instruct model 
  after discussion with the mentor.

- Setting up LM Studio and connecting it to the Python code required understanding how 
  the OpenAI-compatible API works and how to pass environment variables securely using 
  a .env file.

What I Learned

- How to set up a local LLM using LM Studio and connect it to a Python project
- How to use LangChain and LangGraph to build agentic workflows
- How to structure a multi-agent system where each agent has a specific role
- The importance of using environment variables to keep sensitive information secure
- How to use Git and GitHub for version control and project submission

ULLI NAGA SRI VENKATA NAVYA SRI
