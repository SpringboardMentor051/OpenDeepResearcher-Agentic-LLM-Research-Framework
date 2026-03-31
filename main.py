from graph.pipeline import build_graph

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
    return result["final_report"]
