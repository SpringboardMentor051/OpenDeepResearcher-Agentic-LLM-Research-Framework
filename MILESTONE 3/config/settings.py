import os
from dotenv import load_dotenv

load_dotenv()

# ---- LLM Configuration ----
LLM_URL = os.getenv("LLM_URL", "http://127.0.0.1:1234")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5-coder-7b-instruct")
LLM_API_KEY = os.getenv("LLM_API_KEY", "lm-studio")

# ---- Tavily Configuration ----
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# ---- Agent Configuration ----
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
RESEARCH_DEPTH = int(os.getenv("RESEARCH_DEPTH", "3"))

# ---- Pipeline Configuration ----
TIMEOUT = int(os.getenv("TIMEOUT", "30"))