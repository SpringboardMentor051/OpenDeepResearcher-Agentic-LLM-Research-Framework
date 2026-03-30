from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not found in .env file")

tavily = TavilyClient(api_key=TAVILY_API_KEY)


def search_web(query: str):
    try:
        response = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=3
        )

        results = response.get("results", [])

        if not results:
            print("No results found.")
            return []

        output = []

        for i, result in enumerate(results, 1):
            title = result.get("title", "No Title")
            content = result.get("content", "")[:500]
            url = result.get("url", "No URL")

            print(f"\nResult {i}")
            print(f"Title  : {title}")
            print(f"Source : {url}")

            output.append({
                "title": title,
                "url": url,
                "content": content
            })

        return output

    except Exception as e:
        print("Search Error:", str(e))
        return []