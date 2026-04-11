from milestone2.graph.pipeline import full_pipeline

def run_pipeline(query, chat_history=None):

    if chat_history:
        context = "\n".join(
            [f"{m['role']}: {m['content']}" for m in chat_history[-2:]]
        )
        query = f"{context}\n\nUser: {query}"

    result = full_pipeline(query)

    report = result.get("report", "")
    research = result.get("research", [])

    # 🔥 EXTRACT SOURCES
    sources = []
    for item in research:
        for s in item.get("sources", []):
            sources.append({
                "title": s.get("title", ""),
                "url": s.get("url", "")
            })

    return {
        "report": report,
        "sources": sources
    }