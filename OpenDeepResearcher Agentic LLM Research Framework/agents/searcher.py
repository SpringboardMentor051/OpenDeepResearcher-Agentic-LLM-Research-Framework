import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()


class SearcherAgent:
    def __init__(self):
        self.client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    def search(self, query: str):
        response = self.client.search(
            query=query,
            search_depth="basic",
            max_results=3
        )

        results = []

        for result in response["results"]:
            results.append({
                "title": result["title"],
                "url": result["url"],
                "content": result["content"]
            })

        return results