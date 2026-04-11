from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_agent(question):

    response = tavily.search(
        query=question,
        search_depth="advanced",
        max_results=2   # 🔥 keep small for speed
    )

    results = []

    for r in response["results"]:
        results.append({
            "title": r["title"],
            "url": r["url"],
            "content": r["content"][:150]
        })

    return results