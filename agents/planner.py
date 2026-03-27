

from openai import OpenAI
import os
class Planner:
    def __init__(self, model_name: str, base_url: str):
        self.client = OpenAI(
            base_url=base_url,
            api_key=os.getenv("API_KEY")
        )
        self.model = model_name

    def create_plan(self, user_query: str) -> list:
        prompt =  f"""
Break the topic into exactly 4 research questions.

Topic:
{user_query}

STRICT RULES:
- Exactly 4 questions
- No explanations
- No text before or after
- No numbering
Write exactly 4 short research questions, one per line.
No numbering. No labels.

"""


        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a research planning assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
         )

        content =response.choices[0].message.content
        sub_questions = [
            line.strip()
            for line in content.split("\n")
            if line.strip()
        ]
        return sub_questions
