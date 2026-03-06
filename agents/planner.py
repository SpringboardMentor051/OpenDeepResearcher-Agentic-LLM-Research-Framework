from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

class PlannerAgent:

    def __init__(self):

        self.client = OpenAI(
            base_url=os.getenv("BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.model = os.getenv("MODEL_NAME")

    def plan(self, topic):

        system_prompt = """
You are a research planner.
Break the topic into useful search questions.
"""

        try:

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": topic}
                ],
                temperature=0.7,
                max_tokens=200
            )

            return response.choices[0].message.content

        except Exception as e:

            return f"Planner error: {e}"