from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END

from agents.planner import PlannerAgent
from agents.searcher import SearcherAgent
from agents.writer import WriterAgent


# -----------------------------
# STATE DEFINITION
# -----------------------------
class ResearchState(TypedDict):
    topic: str
    questions: List[str]
    research_data: Dict[str, List[dict]]
    final_report: str


# -----------------------------
# AGENTS INIT (load once)
# -----------------------------
planner = PlannerAgent()
searcher = SearcherAgent()
writer = WriterAgent()


# -----------------------------
# PLANNER NODE
# -----------------------------
def planner_node(state: ResearchState):
    print("🧠 Planning research questions...")

    questions = planner.create_plan(state["topic"])

    # safety fallback
    if not questions:
        questions = [state["topic"]]

    # limit for speed
    questions = questions[:3]

    return {
        **state,
        "questions": questions
    }


# -----------------------------
# SEARCH NODE
# -----------------------------
def search_node(state: ResearchState):
    print("🔍 Searching information...")

    research_data = {}

    for q in state["questions"]:
        print(f"   → {q}")

        results = searcher.search(q)

        # safety fallback
        research_data[q] = results if results else []

    return {
        **state,
        "research_data": research_data
    }


# -----------------------------
# WRITER NODE
# -----------------------------
def writer_node(state: ResearchState):
    print("✍️ Generating final report...")

    report = writer.write_report(
        topic=state["topic"],
        research_dict=state["research_data"]
    )

    return {
        **state,
        "final_report": report
    }


# -----------------------------
# GRAPH BUILD (ONCE ONLY)
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


app = build_graph()


# -----------------------------
# MAIN RUN FUNCTION
# -----------------------------
def run_research(topic: str):
    try:
        result = app.invoke({
            "topic": topic,
            "questions": [],
            "research_data": {},
            "final_report": ""
        })

        return result.get("final_report", "No report generated")
    except Exception as e:
        return f"""
    
⚠️ System Error (Handled Safely)

Reason: {str(e)}

Fix Suggestions:
- Ensure Ollama is running: `ollama serve`
- Check internet connection (Tavily API)
- Retry request

Note: UI is working correctly, backend temporarily failed.
"""

# -----------------------------
# CLI ENTRY (testing only)
# -----------------------------
if __name__ == "__main__":

    topic = input("Enter research topic: ")

    print("\n🚀 Running AI Research Agent...\n")

    report = run_research(topic)

    print("\n========== FINAL REPORT ==========\n")
    print(report)