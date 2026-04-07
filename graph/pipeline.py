from typing import TypedDict, List, Optional
from openai import OpenAI
from agents.planner import Planner
from agents.searcher import Searcher
from agents.writer import Writer
from langgraph.graph import StateGraph, END
import os
import concurrent.futures
from dotenv import load_dotenv

load_dotenv()


class ResearchState(TypedDict):
    query: str
    history: List[dict]
    sub_questions: List[str]
    partial_summaries: List[str]
    final_report: str
    is_followup: bool
    error: Optional[str]


# ──────────────────────────────────────────
# FOLLOW-UP DETECTOR
# ──────────────────────────────────────────
def detect_followup_llm(state: ResearchState) -> dict:
    if not state["history"]:
        return {"is_followup": False}

    recent_history = state["history"][-6:]
    history_text = "\n".join([
        f"{msg['role']}: {msg['content'][:200]}"
        for msg in recent_history
    ])

    prompt = f"""
Prior conversation:
{history_text}

New query: {state["query"]}

Does the new query ask about a specific aspect, benefit, detail, or follow-on of what was previously discussed?

Answer ONLY: YES or NO
"""

    try:
        response = OpenAI(
            api_key=os.getenv("API_KEY"),
            base_url=os.getenv("BASE_URL")
        ).chat.completions.create(
            model=os.getenv("MODEL_NAME"),
            messages=[
                {"role": "system", "content": "You answer only YES or NO."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            timeout=15
        )
        text = response.choices[0].message.content.strip().upper()
        return {"is_followup": "YES" in text}
    except Exception:
        return {"is_followup": False}


# ──────────────────────────────────────────
# PLANNER
# ──────────────────────────────────────────
def planner_node(state: ResearchState) -> dict:
    try:
        planner = Planner(os.getenv("MODEL_NAME"), os.getenv("BASE_URL"))
        sub_questions = planner.create_plan(
            state["query"],
            state["history"],
            state["is_followup"]
        )
        return {
            "sub_questions": sub_questions,
            "partial_summaries": []
        }
    except Exception as e:
        return {
            "sub_questions": [state["query"]],
            "partial_summaries": [],
            "error": f"Planner error: {e}"
        }


# ──────────────────────────────────────────
# PARALLEL SEARCHER + WRITER
# ──────────────────────────────────────────
def _search_and_write_one(question: str, history: list, is_followup: bool) -> str:
    """Search and write for a single sub-question. Runs in a thread."""
    searcher = Searcher()
    writer = Writer(os.getenv("MODEL_NAME"), os.getenv("BASE_URL"))

    try:
        results = searcher.search(question)
        formatted = searcher.format_results(results)
    except Exception as e:
        formatted = f"Search error: {e}"

    try:
        summary = writer.summarize(
            sub_question=question,
            search_content=formatted,
            history=history,
            is_followup=is_followup,
            final=False
        )
    except Exception as e:
        summary = f"Writing error: {e}"

    return f"### {question}\n{summary}"


def parallel_search_write_node(state: ResearchState) -> dict:
    """Run all 4 sub-questions in parallel using ThreadPoolExecutor."""
    questions = state["sub_questions"]
    history = state["history"]
    is_followup = state["is_followup"]

    partial_summaries = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(_search_and_write_one, q, history, is_followup): q
            for q in questions
        }
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result(timeout=90)
                partial_summaries.append(result)
            except Exception as e:
                q = futures[future]
                partial_summaries.append(f"### {q}\n[Error processing this question: {e}]")

    return {"partial_summaries": partial_summaries}


# ──────────────────────────────────────────
# FINAL WRITER
# ──────────────────────────────────────────
def final_writer_node(state: ResearchState) -> dict:
    try:
        writer = Writer(os.getenv("MODEL_NAME"), os.getenv("BASE_URL"))
        combined = "\n\n".join(state["partial_summaries"])
        final_summary = writer.summarize(
            sub_question=state["query"],
            search_content=combined,
            history=state["history"],
            is_followup=state["is_followup"],
            final=True
        )
        return {"final_report": final_summary}
    except Exception as e:
        return {
            "final_report": f"❌ Final report generation failed: {e}\n\n"
                            + "\n\n".join(state["partial_summaries"])
        }


# ──────────────────────────────────────────
# BUILD GRAPH
# ──────────────────────────────────────────
def build_graph():
    builder = StateGraph(ResearchState)

    builder.add_node("followup_detector", detect_followup_llm)
    builder.add_node("planner", planner_node)
    builder.add_node("parallel_research", parallel_search_write_node)
    builder.add_node("final_writer", final_writer_node)

    builder.set_entry_point("followup_detector")
    builder.add_edge("followup_detector", "planner")
    builder.add_edge("planner", "parallel_research")
    builder.add_edge("parallel_research", "final_writer")
    builder.add_edge("final_writer", END)

    return builder.compile()