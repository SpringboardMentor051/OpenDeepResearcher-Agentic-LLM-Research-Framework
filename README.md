# OpenDeepResearcher-Agentic-LLM-Research-Framework

Welcome to OpenDeepResearcher, an open research framework designed for building and experimenting with Agentic Large Language Model (LLM) systems.

This repository is intended for submitting research implementations, experimental projects, and autonomous agent-based LLM systems.
## For submissions:-
### Step1:- Click on the main button
### Step2:- Type your name in box and click on create branch
### Step3:- Submit your code in that branch only

## Simple Agentic Research Pipeline

Implemented files:

- `opensearch/planner.py`: Planner Agent (breaks topic into queries)
- `opensearch/searcher.py`: Searcher Agent (fetches content via Tavily)
- `opensearch/writer.py`: Writer Agent (synthesizes summary using LLM)
- `main.py`: LangGraph execution pipeline

### Setup

```bash
pip install -r requirements.txt
export TAVILY_API_KEY="your_tavily_key"
export OPENAI_API_KEY="lm-studio"  # optional dummy value for local server
```

Optional for local model servers:

```bash
export OPENAI_BASE_URL="http://localhost:1234/v1"
export OPENAI_MODEL="qwen/qwen3.5-9b"
```

### Validate loop (input -> summary)

```bash
python main.py --validate
```

Or with your topic:

```bash
python main.py "Latest trends in agentic LLM systems"
```
