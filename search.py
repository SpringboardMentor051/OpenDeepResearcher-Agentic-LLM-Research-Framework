from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from .config import Settings


class SearchError(RuntimeError):
    pass


@dataclass
class TavilyClient:
    settings: Settings

    def search(self, query: str, max_results: int = 3) -> list[dict[str, str]]:
        if not self.settings.tavily_api_key:
            return [
                {
                    "title": "Stub result (no Tavily key configured)",
                    "url": "https://example.com",
                    "content": "Add TAVILY_API_KEY in .env to enable real-time web search.",
                }
            ]

        payload = {
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
            "include_answer": False,
            "include_raw_content": False,
        }
        payload_with_key = {
            **payload,
            "api_key": self.settings.tavily_api_key,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.tavily_api_key}",
            "Content-Type": "application/json",
        }

        try:
            # Try current Tavily auth style first (Bearer token in header).
            response = requests.post(
                "https://api.tavily.com/search",
                json=payload,
                headers=headers,
                timeout=30,
            )
            if response.status_code == 400:
                # Backward-compatible retry for payload api_key style.
                response = requests.post(
                    "https://api.tavily.com/search",
                    json=payload_with_key,
                    timeout=30,
                )
            response.raise_for_status()
            body: dict[str, Any] = response.json()
            results = body.get("results", [])
            cleaned: list[dict[str, str]] = []
            for item in results:
                cleaned.append(
                    {
                        "title": str(item.get("title", "")),
                        "url": str(item.get("url", "")),
                        "content": str(item.get("content", "")),
                    }
                )
            return cleaned
        except Exception as exc:
            if self.settings.tavily_stub_on_error:
                return [
                    {
                        "title": "Stub result (Tavily request failed)",
                        "url": "https://example.com",
                        "content": (
                            "Tavily request failed and fallback was used. "
                            f"Error: {exc}"
                        ),
                    }
                ]
            raise SearchError(f"Tavily request failed: {exc}") from exc
