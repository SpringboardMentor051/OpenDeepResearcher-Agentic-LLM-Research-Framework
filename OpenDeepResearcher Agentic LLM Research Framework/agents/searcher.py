import os
from tavily import TavilyClient
from dotenv import load_dotenv
from halo import Halo

load_dotenv()


class SearcherAgent:
    def __init__(self):
        self.client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    def search(self, query: str):

        # Prevent invalid or very short queries
        if not query or len(query.strip()) < 3:
            return []

        response = self.client.search(
            query=query,
            search_depth="basic",
            max_results=5
        )

        results = []

        for result in response["results"]:

            title = result.get("title", "")
            url = result.get("url", "")
            content = result.get("content", "")

            # ✅ Skip empty content only (safe)
            if not content or len(content.strip()) < 40:
                continue

            # ✅ SAFE REPLACEMENT FOR OVER-STRICT FILTER
            query_words = query.lower().split()

            match_score = 0
            for word in query_words:
                if word in title.lower():
                    match_score += 2
                if word in content.lower():
                    match_score += 1

            if match_score < 2:
                continue

            # ✅ Reduce content size (faster processing)
            if len(content) > 800:
                content = content[:800] + "..."

            results.append({
                "title": title.strip(),
                "url": url.strip(),
                "content": content.strip()
            })

        return results


# -------- RUN INDIVIDUALLY --------

if __name__ == "__main__":

    searcher = SearcherAgent()

    query = input("Enter search query: ")

    spinner = Halo(text="Searching the web...", spinner="dots")
    spinner.start()

    results = searcher.search(query)

    spinner.stop()
    print("Search completed")
    print("\nResults:\n")

    for r in results:
        print("Title: **" + r["title"] + "**")
        print("Source:", r["url"])
        print("Content:", r["content"])
        print("\n-----------------\n")