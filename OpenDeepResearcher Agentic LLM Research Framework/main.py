from agents.searcher import SearcherAgent

if __name__ == "__main__":
    searcher = SearcherAgent()

    results = searcher.search("Impact of Artificial Intelligence in Healthcare")

    for r in results:
        print("\nTitle:", r["title"])
        print("URL:", r["url"])
        print("Content Preview:", r["content"][:200])