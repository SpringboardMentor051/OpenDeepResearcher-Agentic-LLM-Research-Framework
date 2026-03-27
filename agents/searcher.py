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


    def format_results(self,results):
        formatted = ""
        for r in results:
            formatted += f"""
    Title: {r.get('title')}
    Content: {r.get('content')}
    URL: {r.get('url')}
    ---
    """
        return formatted

    def search(self, query: str, max_results: int = 3) -> List[Dict]:
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results
            )
        except Exception as e:
            raise RuntimeError(f"Tavily search failed: {e}")

        return response.get("results")
    
if __name__=="__main__":
    from planner import Planner
    prompt="Snapdragon 888 smartphone performance camera battery features"
    sub_questions=Planner(os.getenv("MODEL_NAME"),os.getenv("BASE_URL")).create_plan(prompt)
    
    searcher = Searcher()
    for question in sub_questions:
        results = searcher.search(
            query=question,
        max_results=5
    )
        for r in results:
            print("Title:", r.get("title"))
            print("URL:", r.get("url"))
            print("Content:", r.get("content"))
            print("-" * 50)

    

