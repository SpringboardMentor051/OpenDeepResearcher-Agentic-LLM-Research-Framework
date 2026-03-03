# agents/searcher.py

from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

class Searcher:
    def __init__(self):
        self.client = TavilyClient(
            api_key=os.getenv("TAVILY_API_KEY")
        )

    def search(self, query: str) -> str:
        response = self.client.search(query)

        results = response.get("results", [])

        if not results:
            return "No relevant results found."

        # Combine top 2 results
        combined_content = ""
        for result in results[:2]:
            combined_content += result.get("content", "") + "\n"

        return combined_content