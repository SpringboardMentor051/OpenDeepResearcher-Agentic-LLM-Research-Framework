# agents/writer.py

from openai import OpenAI

class Writer:
    def __init__(self, model_name: str, base_url: str):
        self.client = OpenAI(
            base_url=base_url,
            api_key="lm-studio"
        )
        self.model = model_name

    def summarize(self, sub_question: list, search_content: str) -> str:
        prompt = f"""
You are a research writer.

Sub-question:
{sub_question}

Content:
{search_content}

Write a clear, structured summary answering the sub-question.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You write structured research summaries."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content