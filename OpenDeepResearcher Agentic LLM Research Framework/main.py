from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END

# Correct imports (IMPORTANT)
from agents.planner import PlannerAgent
from agents.searcher import SearcherAgent
from agents.writer import WriterAgent


# -----------------------------
# 1. Define State
# -----------------------------
class ResearchState(TypedDict):
    topic: str
    questions: List[str]
    research_data: Dict[str, List[dict]]
    final_report: str


# -----------------------------
# 2. Initialize Agents
# -----------------------------
planner = PlannerAgent()
searcher = SearcherAgent()
writer = WriterAgent()


# -----------------------------
# 3. Define Nodes
# -----------------------------
def planner_node(state: ResearchState):
    print("🧠 Generating research plan...")
    questions = planner.create_plan(state["topic"])
    return {**state, "questions": questions}


def search_node(state: ResearchState):
    print("🔍 Searching for information...")
    research_data = {}

    for q in state["questions"]:
        print(f"   → {q}")
        results = searcher.search(q)
        research_data[q] = results

    return {**state, "research_data": research_data}


def writer_node(state: ResearchState):
    print("✍️ Writing final report...")
    report = writer.write_report(
        topic=state["topic"],
        research_dict=state["research_data"]
    )
    return {**state, "final_report": report}


# -----------------------------
# 4. Build Graph
# -----------------------------
def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("planner", planner_node)
    graph.add_node("searcher", search_node)
    graph.add_node("writer", writer_node)

    graph.set_entry_point("planner")

    graph.add_edge("planner", "searcher")
    graph.add_edge("searcher", "writer")
    graph.add_edge("writer", END)

    return graph.compile()


# -----------------------------
# 5. Run App
# -----------------------------
def run_research(topic: str):
    app = build_graph()

    result = app.invoke({
        "topic": topic,
        "questions": [],
        "research_data": {},
        "final_report": ""
    })

    return result["final_report"]


# -----------------------------
# 6. Entry Point
# -----------------------------
if __name__ == "__main__":
    topic = input("Enter research topic: ")

    print("\n🚀 Running AI Research Agent...\n")

    report = run_research(topic)

    print("\n========== FINAL REPORT ==========\n")
    print(report)