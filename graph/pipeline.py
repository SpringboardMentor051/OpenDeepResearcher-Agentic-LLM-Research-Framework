from typing import TypedDict, List
from agents.planner import Planner
from agents.searcher import Searcher
from agents.writer import Writer
from langgraph.graph import StateGraph, END
import os
from dotenv import load_dotenv

load_dotenv()


class ResearchState(TypedDict):
    query: str
    history: List[dict]   # ✅ MEMORY ADDED
    sub_questions: List[str]
    current_question: str
    search_results: str
    partial_summaries: List[str]
    final_report: str


# ----------------------
# PLANNER
# ----------------------
def planner_node(state: ResearchState):
    planner = Planner(os.getenv('MODEL_NAME'), os.getenv('BASE_URL'))

    return {
        "sub_questions": planner.create_plan(state["query"]),
        "partial_summaries": []
    }


# ----------------------
# ROUTER
# ----------------------
def router_node(state: ResearchState):
    if not state["sub_questions"]:
        return {}

    return {
        "current_question": state["sub_questions"][0],
        "sub_questions": state["sub_questions"][1:]
    }


# ----------------------
# SEARCHER
# ----------------------
def format_results(results, max_chars=500):
    chunks = []

    for r in results[:3]:
        content = r.get("content", "")
        title = r.get("title", "")

        if not content:
            continue

        chunks.append(f"Title: {title}\nContent: {content[:max_chars]}")

    return "\n\n".join(chunks)


def searcher_node(state: ResearchState):
    try:
        searcher = Searcher()
        results = searcher.search(state["current_question"])
        formatted = format_results(results)
    except Exception as e:
        formatted = f"Search failed: {str(e)}"

    return {
        "search_results": formatted
    }


# ----------------------
# WRITER (PARTIAL — NO MEMORY)
# ----------------------
def writer_node(state: ResearchState):
    writer = Writer(os.getenv('MODEL_NAME'), os.getenv('BASE_URL'))
    # ✅ Windowed memory
 

    summary = writer.summarize(state["current_question"],state["search_results"],state["history"])

    return {
        "partial_summaries": state["partial_summaries"] + [
            f"{state['current_question']}\n{summary}"
        ]
    }


# ----------------------
# FINAL WRITER (MEMORY HERE)
# ----------------------
def final_writer_node(state: ResearchState):
    writer = Writer(os.getenv('MODEL_NAME'), os.getenv('BASE_URL'))

    combined = "\n\n".join(state["partial_summaries"])

    final_summary=writer.summarize(state["query"],state["partial_summaries"],state["history"])
    return {
        "final_report": final_summary
    }


# ----------------------
# BUILD GRAPH
# ----------------------
def build_graph():
    builder = StateGraph(ResearchState)

    builder.add_node("planner", planner_node)
    builder.add_node("router", router_node)
    builder.add_node("searcher", searcher_node)
    builder.add_node("writer", writer_node)
    builder.add_node("final_writer", final_writer_node)

    builder.set_entry_point("planner")

    builder.add_edge("planner", "router")

    builder.add_conditional_edges(
        "router",
        lambda state: "final_writer" if not state["sub_questions"] else "searcher"
    )

    builder.add_edge("searcher", "writer")
    builder.add_edge("writer", "router")

    builder.add_edge("final_writer", END)

    return builder.compile()
