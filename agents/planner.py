

from openai import OpenAI
import os

class Planner:
    def __init__(self, model_name: str, base_url: str):
        self.client = OpenAI(
            base_url=base_url,
            api_key="lm-studio"
        )
        self.model = model_name

    def create_plan(self, user_query: str) -> list:
        prompt = f"""
Break the following research topic into 5 clear sub-questions.

Topic: {user_query}

Return only a numbered list.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a research planning assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content

        # Simple parsing into list
        sub_questions = [
            line.strip()
            for line in content.split("\n")
            if line.strip()
        ]

        return sub_questions