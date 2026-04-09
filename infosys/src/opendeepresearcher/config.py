from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


# Always load the backend-local .env (infosys/.env), then allow ambient env vars.
BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_ROOT / ".env")
load_dotenv()


@dataclass(frozen=True)
class Settings:
	llm_provider: str = field(
		default_factory=lambda: os.getenv("LLM_PROVIDER", "ollama").strip().lower()
	)
	llm_model: str = field(
		default_factory=lambda: os.getenv("LLM_MODEL", "google/gemma-3-4b").strip()
	)
	llm_base_url: str = field(
		default_factory=lambda: os.getenv("LLM_BASE_URL", "http://10.79.241.47:1234").strip()
	)
	llm_api_key: str = field(default_factory=lambda: os.getenv("LLM_API_KEY", "").strip())
	llm_timeout_seconds: int = field(
		default_factory=lambda: int(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
	)
	quick_answer_search_max_results: int = field(
		default_factory=lambda: int(os.getenv("QUICK_ANSWER_SEARCH_MAX_RESULTS", "3"))
	)
	quick_answer_skip_search: bool = field(
		default_factory=lambda: os.getenv("QUICK_ANSWER_SKIP_SEARCH", "false").strip().lower() == "true"
	)
	llm_stub_on_error: bool = field(
		default_factory=lambda: os.getenv("LLM_STUB_ON_ERROR", "true").strip().lower() == "true"
	)
	tavily_stub_on_error: bool = field(
		default_factory=lambda: os.getenv("TAVILY_STUB_ON_ERROR", "true").strip().lower() == "true"
	)
	tavily_api_key: str = field(default_factory=lambda: os.getenv("TAVILY_API_KEY", "").strip())


def get_settings() -> Settings:
	# Refresh backend .env so long-running sessions pick up model changes.
	load_dotenv(BACKEND_ROOT / ".env", override=True)
	return Settings()
