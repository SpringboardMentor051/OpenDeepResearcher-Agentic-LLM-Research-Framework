from agents.planner import PlannerAgent
from agents.searcher import SearcherAgent

planner = PlannerAgent()
searcher = SearcherAgent()

print("="*60)
print("OpenDeepResearcher")
print("Planner + Tavily Search")
print("="*60)

while True:

    topic = input("\nEnter research topic: ")

    if topic.lower() in ["exit","quit","q"]:
        break

    print("\n🧠 Planning research...")

    plan = planner.plan(topic)

    print("\nPlanner Output:\n")
    print(plan)

    print("\n🌐 Searching Web using Tavily...\n")

    results = searcher.search(topic)

    for r in results:
        print("-", r[:200])