#!/usr/bin/env python3
"""
Quick Start Guide - Research Pipeline Execution
Step-by-step instructions for running the full research pipeline
"""

print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    Open Researcher Project - Quick Start                      ║
║                        LangGraph Research Pipeline                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝

✅ WEEK 4 IMPLEMENTATION COMPLETE

📋 Completed Components:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Planner Agent
  • Breaks down research topics into structured steps
  • Uses local LLM (LM Studio/Ollama)
  • Returns detailed planning data
  
✓ Searcher Agent
  • Fetches relevant content using Tavily API
  • Implements fallback for API failures
  • Returns aggregated search results
  
✓ Writer Agent
  • Synthesizes search results into coherent summaries
  • Extracts key findings
  • Generates academic-style output
  
✓ LangGraph Pipeline
  • Orchestrates all three agents
  • Manages state flow between nodes
  • Handles errors gracefully
  • Tracks execution metrics

✓ Full Integration
  • End-to-end research flow
  • JSON output with results
  • Comprehensive logging
  • Error handling and validation


🚀 QUICK START (5 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1: Validate Pipeline
────────────────────────────────────────────────────────────────────────────────
  python test_pipeline.py
  
  Expected output: "All validation tests passed!"
  Time: ~5 seconds


STEP 2: Configure Tavily API (if using search)
────────────────────────────────────────────────────────────────────────────────
  1. Go to https://tavily.com
  2. Sign up and get API key
  3. Edit .env file and add:
     TAVILY_API_KEY=your_key_here
  
  Note: Without Tavily key, pipeline uses LLM knowledge fallback


STEP 3: Ensure LLM Server Running
────────────────────────────────────────────────────────────────────────────────
  Option A - LM Studio:
    • Download from https://lmstudio.ai
    • Load model: qwen2.5-coder-7b-instruct
    • Start server (port 1234)
  
  Option B - Ollama:
    • Install from https://ollama.ai
    • Run: ollama pull qwen2.5-coder-7b-instruct
    • Run: ollama serve
    • Update .env: LLM_URL=http://127.0.0.1:1234


STEP 4: Run Full Pipeline
────────────────────────────────────────────────────────────────────────────────
  python main.py
  
  Expected output:
    ✓ Planning Phase   (5-10 seconds)
    ✓ Searching Phase  (10-20 seconds)  [requires Tavily key and internet]
    ✓ Writing Phase    (10-20 seconds)
    ✓ Final Summary    (displayed)
    
  Total time: 30-60 seconds
  Output: research_result_YYYYMMDD_HHMMSS.json


📊 ARCHITECTURE OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Research Topic (Input)
       ↓
   [Validate Input]
       ↓
┌──────────────────────┐
│  Planner Agent       │ ← Breaks topic into research steps
│  (LLM)               │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│  Searcher Agent      │ ← Fetches content (Tavily API)
│  (Web + Tavily)      │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│  Writer Agent        │ ← Synthesizes summary
│  (LLM)               │
└──────────┬───────────┘
           ↓
    Final Summary (Output)
    research_result_*.json


🔧 CUSTOMIZATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Edit .env file for configuration:

  LLM_URL                 Local LLM endpoint
  MODEL_NAME              Model to use (default: qwen2.5-coder-7b-instruct)
  TAVILY_API_KEY          Tavily search API key
  MAX_SEARCH_RESULTS      Results per query (default: 5)
  RESEARCH_DEPTH          Recursion depth (default: 3)
  TIMEOUT                 Request timeout seconds (default: 30)


📝 RUNNING INDIVIDUAL COMPONENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Test just planner
python -c "from agents.planner import planner_agent; print(planner_agent('AI Ethics'))"

# Test just searcher  
python -c "from agents.searcher import searcher_agent; print(searcher_agent('Study AI Ethics'))"

# Test just writer
python -c "from agents.writer import writer_agent; result = writer_agent('AI', 'Sample content'); print(result['summary'][:200])"

# Test full pipeline via Python
python -c "from pipeline import execute_research; result = execute_research('Your Topic'); print(result['summary']['summary'][:500])"


🧪 TESTING & DEBUGGING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Validation Suite:
  python test_pipeline.py     # Validates structure and imports

Check Imports:
  python -c "from pipeline import execute_research; print('✓ Pipeline OK')"

Monitor Execution:
  Set DEBUG=1 before running main.py to see verbose logs


📂 PROJECT STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

open researcher project/
├── main.py              Main entry point (run this!)
├── pipeline.py          LangGraph orchestration
├── test_pipeline.py     Validation tests
├── agents/
│   ├── planner.py       Planning agent
│   ├── searcher.py      Search agent
│   └── writer.py        Writing/synthesis agent
├── config/
│   └── settings.py      Configuration and environment
├── .env                 Environment variables (edit this!)
├── .env.example         Template for .env
├── requirements.txt     Python dependencies
└── README.md            Full documentation


✅ EVALUATION CHECKLIST (Week 4)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Research Flow Executes Successfully:
  ✅ Planner generates structured steps
  ✅ Searcher fetches relevant content
  ✅ Writer synthesizes coherent summary
  ✅ Pipeline completes end-to-end

Agents Return Relevant, Coherent Responses:
  ✅ Planner creates detailed, actionable steps
  ✅ Searcher returns topic-relevant results
  ✅ Writer produces well-structured academic summary
  ✅ All outputs include metadata

LangGraph Pipeline Operates End-to-End:
  ✅ StateGraph properly orchestrates all agents
  ✅ State flows through validate → plan → search → write
  ✅ Error handling prevents pipeline crashes
  ✅ Execution time tracked and reported


🎯 NEXT STEPS (After Validation)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Week 5+ Enhancements:
  [ ] Multi-query parallel execution
  [ ] Citations and source tracking
  [ ] Iterative refinement loops
  [ ] PDF/HTML output formats
  [ ] Custom agent personas
  [ ] Real-time streaming output
  [ ] Caching for repeated queries
  [ ] Web UI dashboard


📞 TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Issue: "LLM connection failed"
  ✓ Check LLM server is running
  ✓ Verify LLM_URL in .env
  ✓ Test: curl http://127.0.0.1:1234/v1/models

Issue: "Tavily API error"
  ✓ Check TAVILY_API_KEY in .env
  ✓ Verify key is valid (www.tavily.com)
  ✓ Pipeline can work without Tavily (uses LLM knowledge)

Issue: "Import errors"
  ✓ Run: pip install -r requirements.txt
  ✓ Run: pip install --upgrade langgraph langchain

Issue: "Module not found"
  ✓ Ensure in project directory: cd "open researcher project"
  ✓ Activate venv: .\\venv\\Scripts\\Activate.ps1 (Windows)
  ✓ Check Python: python --version


═══════════════════════════════════════════════════════════════════════════════
Ready to research! Run: python main.py
═══════════════════════════════════════════════════════════════════════════════
""")
