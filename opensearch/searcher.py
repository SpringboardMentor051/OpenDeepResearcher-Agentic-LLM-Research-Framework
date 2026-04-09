from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()


tavily = TavilyClient(api_key=os.getenv("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"))

def search(query):

    print("\nSearching:", query)

    try:
        results = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=3
        )
    except Exception as e:
        print("Tavily search failed:", e)
        return ""

    collected_text = ""

    for i, r in enumerate(results.get("results", []), 1):

        title = r.get("title", "")
        url = r.get("url", "")
        content = r.get("content", "")

        # Skip weak or irrelevant results
        if len(content) < 50:
            continue

        print(f"\nSource {i}")
        print("Title:", title)
        print("URL:", url)
        print("Summary:", content[:200], "...")

        collected_text += content + "\n"

    return collected_text













