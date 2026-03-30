from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# Always load the backend-local .env (infosys/.env), then allow ambient env vars.
BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_ROOT / ".env")
load_dotenv()


@dataclass(frozen=True)
class Settings:
	llm_provider: str = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
	llm_model: str = os.getenv("LLM_MODEL", "google/gemma-3-4b").strip()
	llm_base_url: str = os.getenv("LLM_BASE_URL", "http://10.79.241.47:1234").strip()
	llm_api_key: str = os.getenv("LLM_API_KEY", "").strip()
	llm_timeout_seconds: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
	llm_stub_on_error: bool = (
		os.getenv("LLM_STUB_ON_ERROR", "true").strip().lower() == "true"
	)
	tavily_stub_on_error: bool = (
		os.getenv("TAVILY_STUB_ON_ERROR", "true").strip().lower() == "true"
	)
	tavily_api_key: str = os.getenv("TAVILY_API_KEY", "").strip()


def get_settings() -> Settings:
	return Settings()
