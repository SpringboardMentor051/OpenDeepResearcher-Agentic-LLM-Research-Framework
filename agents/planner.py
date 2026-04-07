from openai import OpenAI
import os
import json
import re


class Planner:
    def __init__(self, model_name: str, base_url: str):
        self.client = OpenAI(base_url=base_url, api_key=os.getenv("API_KEY"))
        self.model = model_name

    def create_plan(self, user_query: str, history: list, is_followup: bool = False) -> list:
        recent_history = history[-6:]
        history_text = "\n".join([
            f"{msg['role']}: {msg['content'][:300]}"
            for msg in recent_history
        ])

        if is_followup:
            prompt = f"""
You are a research planning expert handling a FOLLOW-UP question.

CONVERSATION HISTORY (what was already covered):
{history_text}

NEW FOLLOW-UP QUERY:
{user_query}

TASK:
Generate 4 focused research questions specifically about the NEW aspect the user is asking about.
- DO NOT repeat questions about what was already explained in the conversation
- Each question must explore a distinct NEW angle of the follow-up query
- Build on the existing knowledge — go deeper, not wider
- Questions must be answerable by web search

OUTPUT FORMAT:
Return ONLY a JSON array of 4 strings. No explanation, no preamble.
["...", "...", "...", "..."]
"""
        else:
            prompt = f"""
You are a research planning expert.

USER QUERY:
{user_query}

TASK:
Break this into 4 focused research questions that together fully explore the topic.
- Cover distinct aspects (no overlap)
- Be specific and answerable by web search
- Drive meaningful research

OUTPUT FORMAT:
Return ONLY a JSON array of 4 strings. No explanation, no preamble.
["...", "...", "...", "..."]
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You generate ONLY valid JSON arrays. Nothing else."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            timeout=30
        )

        content = response.choices[0].message.content.strip()
        return self._parse_response(content, user_query)

    def _parse_response(self, content: str, user_query: str) -> list:
        # Layer 1: Direct JSON
        result = self._safe_json_parse(content)
        if result:
            return self._validate(result, user_query)

        # Layer 2: Regex extraction
        result = self._extract_json_array(content)
        if result:
            return self._validate(result, user_query)

        # Layer 3: Line fallback
        result = self._line_fallback(content)
        if result:
            return self._validate(result, user_query)

        # Layer 4: Final fallback
        return [
            f"What is {user_query} and why is it important?",
            f"What are the key components or aspects of {user_query}?",
            f"What are the advantages and use cases of {user_query}?",
            f"What are the future trends related to {user_query}?"
        ]

    def _safe_json_parse(self, text):
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                data = list(data.values())
            if isinstance(data, list):
                return data
        except Exception:
            return None

    def _extract_json_array(self, text):
        match = re.search(r"\[.*?\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                return None
        return None

    def _line_fallback(self, text):
        lines = [
            line.strip("-•1234567890. ").strip()
            for line in text.split("\n")
            if line.strip() and len(line.strip()) > 10
        ]
        return lines[:4] if len(lines) >= 4 else None

    def _validate(self, questions, user_query):
        cleaned = [q.strip() for q in questions if isinstance(q, str) and len(q.strip()) > 5]
        if len(cleaned) < 4:
            fallback = [
                f"What is {user_query}?",
                f"What are the key aspects of {user_query}?",
                f"What are examples and use cases of {user_query}?",
                f"What are challenges and future trends in {user_query}?"
            ]
            cleaned.extend(fallback)
        return cleaned[:4]