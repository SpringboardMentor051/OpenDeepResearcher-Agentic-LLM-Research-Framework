import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")

if not api_key:
    raise ValueError("TAVILY_API_KEY not found in .env")

tavily = TavilyClient(api_key=api_key)

def search_web(query):
    response = tavily.search(
        query=query,
        search_depth="advanced",
        max_results=3
    )
    return response


if __name__ == "__main__":
    result = search_web("Latest AI trends in healthcare 2026")
    print(result)