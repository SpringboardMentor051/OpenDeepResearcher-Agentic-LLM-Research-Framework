import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

class SearcherAgent:

    def __init__(self):

        self.client = TavilyClient(
            api_key=os.getenv("TAVILY_API_KEY")
        )

    def search(self, query):

        response = self.client.search(
            query=query,
            search_depth="advanced",
            max_results=3
        )

        results = []

        for r in response["results"]:
            results.append(r["content"])

        return results