import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


class Searcher:
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        self.client = TavilyClient(api_key=api_key) if api_key else None

    def search_many(self, queries):
        results = []

        if not self.client:
            return [{"title": "Error", "content": "Missing TAVILY_API_KEY"}]

        for q in queries:
            try:
                res = self.client.search(query=q, max_results=2)
                results.extend(res.get("results", []))
            except:
                pass

        return results