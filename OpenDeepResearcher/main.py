from OpenDeepResearcher.graph.pipeline import build_graph

graph = build_graph()


def run_research(query: str, history: list):
    state = {
        "query": query,
        "history": history,
        "sub_questions": [],
        "partial_summaries": [],
        "is_followup": False   # ✅ NEW
    }

    result = graph.invoke(state)
    return {
    "final_answer": result["final_report"],
    "steps": {
        "planning": result.get("sub_questions", []),
        "partials": result.get("partial_summaries", [])
    },
    "is_followup": result.get("is_followup", False)
}
