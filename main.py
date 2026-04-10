from agents.planner import Planner
from agents.searcher import Searcher
from agents.writer import Writer
def research_flow(topic):
    planner = Planner()
    searcher = Searcher()
    writer = Writer()

    queries = planner.plan(topic)
    results = searcher.search_many(queries)
    summary = writer.summarize(topic, results)

    print("\nSUMMARY:\n", summary)

if __name__ == "__main__":
    topic = input("Enter topic: ")
    research_flow(topic)