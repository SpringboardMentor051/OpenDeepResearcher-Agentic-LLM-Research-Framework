from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("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"))

def search(query):

    print("\nSearching:", query)

    results = tavily.search(
        query=query,
        search_depth="advanced",
        max_results=3
    )

    collected_text = ""

    for i, r in enumerate(results["results"], 1):

        title = r["title"]
        url = r["url"]
        content = r["content"]

        print(f"\nSource {i}")
        print("Title:", title)
        print("URL:", url)
        print("Summary:", content[:200], "...")

        collected_text += content + "\n"

    return collected_text













