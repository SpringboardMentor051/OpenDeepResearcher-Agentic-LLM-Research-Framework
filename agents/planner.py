from openai import OpenAI
import os
import json
import re

class Planner:
    def __init__(self, model_name: str, base_url: str):
        self.client = OpenAI(
            base_url=base_url,
            api_key=os.getenv("API_KEY")
        )
        self.model = model_name

    def create_plan(self, user_query: str) -> list:
        prompt = f"""
You are a research planner.

Your job is to generate 4 HIGHLY RELEVANT research questions
based strictly on the user's intent.

User Query:
{user_query}

STRICT RULES:
- Focus ONLY on what the user is asking
- Do NOT include generic questions
- Avoid overlap
- Each question must target a different aspect of the query
- Return ONLY valid JSON

Output:
["q1", "q2", "q3", "q4"]
"""


        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a research planning assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        try:
            sub_questions = json.loads(content)
        except:
            match = re.search(r"\{.*\}|\[.*\]", content, re.DOTALL)
            if match:
                sub_questions = json.loads(match.group())
            else:
                raise ValueError(f"Planner output unusable:\n{content}")

# ✅ Normalize format
        if isinstance(sub_questions, dict):
            sub_questions = list(sub_questions.values())

# ✅ Validate
        if not isinstance(sub_questions, list) or len(sub_questions) != 4:
            raise ValueError(f"Planner did not return exactly 4 questions:\n{sub_questions}")

        return sub_questions

