import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from milestone2.agents.planner import planner_agent
from milestone2.agents.searcher import search_agent
from milestone2.agents.writer import writer_agent
import json
import re


def research_pipeline(query):

    # get planner output
    plan_text = planner_agent(query)

    print("\n--- Planner Output ---")
    print(plan_text)

    # extract JSON safely
    json_match = re.search(r"\{.*\}", plan_text, re.DOTALL)

    if not json_match:
        print("Planner did not return valid JSON")
        print(plan_text)
        return {}

    try:
        plan = json.loads(json_match.group())
    except json.JSONDecodeError:
        print("JSON parsing failed")
        print(plan_text)
        return {}

    research_data = {
        "topic": plan.get("topic", query),
        "research": []
    }

    print("\n--- Sub Questions ---")
    print(plan.get("sub_questions", []))

    # run search for each question
    for q in plan.get("sub_questions", []):

        print("\nSearching Tavily for:", q)

        results = search_agent(q)

        print("Results retrieved:", len(results))

        research_data["research"].append({
            "question": q,
            "sources": results
        })

    print("\n--- Research Data Collected ---")
    print(research_data)

    return research_data


def full_pipeline(query):

    research_data = research_pipeline(query)

    if not research_data:
        print("Research pipeline failed")
        return {
            "report": "",
            "research": []
        }

    print("\n--- Sending Data to Writer Agent ---")

    report = writer_agent(research_data)

    # 🔥 IMPORTANT CHANGE
    return {
        "report": report,
        "research": research_data["research"]   # KEEP SOURCES
    }