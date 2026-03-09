import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


class Searcher:
	def __init__(self):
		api_key = os.getenv("TAVILY_API_KEY")
		self.client = TavilyClient(api_key=api_key) if api_key else None

	def search(self, query: str) -> list[dict]:
		if not self.client:
			return [
				{
					"title": "Missing TAVILY_API_KEY",
					"url": "",
					"content": "Set TAVILY_API_KEY to fetch web content.",
				}
			]

		response = self.client.search(query=query, max_results=3)
		return response.get("results", [])

	def search_many(self, queries: list[str]) -> list[dict]:
		all_results: list[dict] = []
		for query in queries:
			all_results.extend(self.search(query))
		return all_results
