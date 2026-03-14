from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("LM_STUDIO_URL"),
    api_key="lm-studio",
    model=os.getenv("MODEL_NAME"),
    temperature=0.2,
    max_tokens=800
)

def plan_query(topic: str) -> dict:
    prompt = f"""
You are a research planner.
Break this topic into 4-5 clear web search questions.

Return ONLY valid JSON like:
{{"questions": ["question 1", "question 2"]}}

Topic: {topic}

JSON:
"""

    try:
        result = llm.invoke(prompt)
        text = result.content.strip()

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())

    except Exception as e:
        print(f"Planner error: {e}")

    return {"questions": [topic]}