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
    data = search(q)
    if data:   
        research_data += data

history = []   

report = write_report(topic, research_data[:3000], history)

print("\nFINAL RESEARCH REPORT\n")
print(report)












