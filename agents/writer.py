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

    def summarize(self, sub_question: str, search_content: str, history: list, final: bool = False) -> str:

            # Take last N messages only
        recent_history = history[-6:]

        history_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in recent_history
            ])
        if final:
                prompt = f"""
You are a senior research analyst.

Conversation Context:
{history_text}

Main Query:
{sub_question}

Collected Research:
{search_content}

Task:
- Synthesize all findings into a cohesive report

Output Structure:
1. Overview
2. Key Insights
3. Detailed Explanation
4. Conclusion
Rules:
- Use conversation context to resolve ambiguity
- Do NOT repeat previously answered points
- Build on prior responses if relevant
- Remove redundancy
- Merge overlapping ideas
- Be precise and structured
- Do NOT repeat questions
"""

        else:
            prompt = f"""
    You are a professional research analyst.
Conversation Context:
{history_text}

Query:
{sub_question}

Research Findings:
{search_content}

Task:
- Generate a final structured answer
- Use context only if relevant
STRICT INSTRUCTION:
- Only answer what is asked in the query
- Do NOT include unrelated sections
- If query is about advantages → DO NOT include risks
- If query is about risks → DO NOT include benefits
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
    