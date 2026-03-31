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
    history: List[dict]
    sub_questions: List[str]
    current_question: str
    search_results: str
    partial_summaries: List[str]
    final_report: str
    is_followup: bool   # ✅ NEW


# ----------------------
# FOLLOW-UP DETECTOR
# ----------------------
def followup_detector_node(state: ResearchState):
    history = state["history"]

    if len(history) < 2:
        return {"is_followup": False}

    last_user_queries = [
        msg["content"]
        for msg in history
        if msg["role"] == "user"
    ]

    if len(last_user_queries) < 2:
        return {"is_followup": False}

    current_query = last_user_queries[-1].lower()
    previous_query = last_user_queries[-2].lower()

    followup_keywords = [
        "what about", "also", "advantages", "disadvantages",
        "pros", "cons", "why", "how about", "compare", "more"
    ]

    keyword_flag = any(k in current_query for k in followup_keywords)

    overlap = len(set(current_query.split()) & set(previous_query.split()))
    similarity_score = overlap / max(len(current_query.split()), 1)

    if similarity_score > 0.4 or keyword_flag:
        return {"is_followup": True}

    return {"is_followup": False}


# ----------------------
# PLANNER
# ----------------------
def planner_node(state: ResearchState):
    planner = Planner(os.getenv('MODEL_NAME'), os.getenv('BASE_URL'))

    recent_history = state["history"][-6:]
    history_text = "\n".join([
        f"{msg['role']}: {msg['content']}"
        for msg in recent_history
    ])

    enriched_query = f"""
Conversation Context:
{history_text}

Current User Query:
{state["query"]}
"""

    return {
        "sub_questions": planner.create_plan(enriched_query),
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
        url = r.get("url", "")

        if not content:
            continue

        chunks.append(
            f"Title: {title}\nContent: {content[:max_chars]}\nURL: {url}"
        )

    return "\n\n".join(chunks)


def searcher_node(state: ResearchState):
    searcher = Searcher()

    last_user_msgs = [
        msg["content"]
        for msg in state["history"]
        if msg["role"] == "user"
    ]

    context = last_user_msgs[-2:] if last_user_msgs else []

    enriched_query = f"""
Context:
{" ".join(context)}

Question:
{state["current_question"]}
"""

    results = searcher.search(enriched_query)

    if not results:
        raise ValueError(f"No results for: {state['current_question']}")

    formatted = format_results(results)

    return {
        "search_results": formatted
    }


# ----------------------
# WRITER
# ----------------------
def writer_node(state: ResearchState):
    writer = Writer(os.getenv('MODEL_NAME'), os.getenv('BASE_URL'))
    summary = writer.summarize(
        state["current_question"],
        state["search_results"],
        state["history"],
        is_followup=state.get("is_followup", False)
    )

    return {
        "partial_summaries": state["partial_summaries"] + [
            f"{state['current_question']}\n{summary}"
        ]
    }


# ----------------------
# FINAL WRITER
# ----------------------
def final_writer_node(state: ResearchState):
    writer = Writer(os.getenv('MODEL_NAME'), os.getenv('BASE_URL'))

    combined = "\n\n".join(state["partial_summaries"])

    final_summary = writer.summarize(
        state["query"],
        combined,
        state["history"],
        is_followup=state.get("is_followup", False),
        final=True
    )

    return {
        "final_report": final_summary
    }


# ----------------------
# BUILD GRAPH
# ----------------------
def build_graph():
    builder = StateGraph(ResearchState)

    builder.add_node("followup_detector", followup_detector_node)  # ✅ NEW
    builder.add_node("planner", planner_node)
    builder.add_node("router", router_node)
    builder.add_node("searcher", searcher_node)
    builder.add_node("writer", writer_node)
    builder.add_node("final_writer", final_writer_node)

    builder.set_entry_point("followup_detector")  # ✅ UPDATED

    builder.add_edge("followup_detector", "planner")
    builder.add_edge("planner", "router")

    builder.add_conditional_edges(
        "router",
        lambda state: "final_writer" if not state["sub_questions"] else "searcher"
    )

    builder.add_edge("searcher", "writer")
    builder.add_edge("writer", "router")
    builder.add_edge("final_writer", END)

    return builder.compile()
