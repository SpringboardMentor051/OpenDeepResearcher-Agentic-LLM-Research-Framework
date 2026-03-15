from utils.llm import get_llm
import json
import re

llm = get_llm()

def planner_agent(query):

    prompt = f"""
You are a research planner.

Break the topic into 3 research questions.

Return ONLY valid JSON.

Example format:

{{
 "topic": "example",
 "sub_questions": [
   "question1",
   "question2",
   "question3"
 ]
}}

Topic:
{query}
"""

    response = llm.invoke(prompt)

    text = response.content

    # extract JSON block safely
    json_match = re.search(r"\{.*\}", text, re.DOTALL)

    if json_match:
        return json_match.group()

    return text