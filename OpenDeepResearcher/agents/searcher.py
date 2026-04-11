from tavily import TavilyClient
import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()


class Searcher:
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        self.client = TavilyClient(api_key=api_key)

    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results
            )
            results = response.get("results", [])
            if not results:
                # Retry with simpler query
                response = self.client.search(
                    query=query,
                    search_depth="basic",
                    max_results=max_results
                )
                results = response.get("results", [])
            return results
        except Exception as e:
            raise RuntimeError(f"Search failed for '{query}': {e}")

    def format_results(self, results: List[Dict], max_chars: int = 800) -> str:
        if not results:
            return "No search results found."
        chunks = []
        for r in results[:4]:
            content = r.get("content", "").strip()
            title = r.get("title", "No title")
            url = r.get("url", "")
            if not content:
                continue
            chunks.append(f"Title: {title}\nContent: {content[:max_chars]}\nURL: {url}")
        return "\n\n---\n\n".join(chunks) if chunks else "No usable content found."
