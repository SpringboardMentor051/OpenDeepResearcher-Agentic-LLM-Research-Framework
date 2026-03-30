import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

def search_agent(sub_questions):
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    results = []

    for q in sub_questions:
        response = client.search(q)
        content = response.get("results", [])
        
        if content:
            results.append(content[0]["content"])
        else:
            results.append(f"No result for {q}")

    return results