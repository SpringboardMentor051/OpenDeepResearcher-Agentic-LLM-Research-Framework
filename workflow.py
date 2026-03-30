from app.agents.planner import planner_agent
from app.agents.searcher import search_agent
from app.agents.writer import writer_agent
from app.utils.memory import save_memory

def run_workflow(query):
    sub_questions = planner_agent(query)
    results = search_agent(sub_questions)
    summary = writer_agent(results)

    save_memory(query, summary)

    return summary