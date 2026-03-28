from opensearch.planner import plan_research
from opensearch.searcher import search
from opensearch.writer import write_report

topic = input("Enter research topic: ")

# Planner
questions = plan_research(topic)

print("\nGenerated Questions:\n")
for q in questions:
    print(q)

# Searcher
research_data = ""

print("\nSearching web using Tavily...\n")

for q in questions:
    research_data += search(q)

# Writer step
report = write_report(topic, research_data[:3000])

print("\nFINAL RESEARCH REPORT\n")
print(report)













