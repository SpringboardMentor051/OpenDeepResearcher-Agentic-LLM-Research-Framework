# agents/writer.py

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
from os import getenv
class Writer:
    def __init__(self, model_name: str, base_url: str):
        self.client = OpenAI(
            base_url=base_url,
            api_key=getenv("API_KEY")
        )
        self.model = model_name

    def summarize(self, sub_question: list, search_content: str, history:list)->str:

            # Take last N messages only
            recent_history = history[-6:]

            history_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in recent_history
            ])

        
            prompt = f"""
    You are a professional research analyst.
Conversation Context:
{history_text}

User Query:
{sub_question}

Research Findings:
{search_content}

Task:
- Generate a final structured answer
- Use context only if relevant

Rules:
- No redundancy
- No repetition
- Clear structured output
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You write structured research summaries."},
                    {"role": "user", "content": prompt}
                ]
            )

            return response.choices[0].message.content
    