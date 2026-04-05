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

    def create_plan(self, user_query: str,history:list) -> list:
        recent_history=history[-6:]
        history_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in recent_history
        ])

        prompt = f"""
You are a research planning expert.

Your job is to break the user's query into 4 focused research questions that together fully explore the topic.

USER QUERY:
{user_query}

CONVERSATION HISTORY:
{history_text}

TASK:

1. Determine whether the query is:
   - A NEW topic → create broad coverage questions
   - A FOLLOW-UP → extend or deepen previous discussion

2. Generate 4 questions that:
   - Cover distinct aspects (no overlap)
   - Are specific and answerable
   - Drive meaningful research (not definitions unless necessary)

3. For follow-ups:
   - Build on previous context
   - Avoid repeating already explored ideas
   - Go deeper, not wider

OUTPUT FORMAT:
Return ONLY a JSON list of 4 strings.

Example:
["...", "...", "...", "..."]
"""

        # ---------------- API CALL ----------------
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You generate ONLY valid JSON arrays."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        # ---------------- LAYER 1: DIRECT JSON ----------------
        sub_questions = self._safe_json_parse(content)

        # ---------------- LAYER 2: REGEX EXTRACTION ----------------
        if sub_questions is None:
            sub_questions = self._extract_json_array(content)

        # ---------------- LAYER 3: LINE FALLBACK ----------------
        if sub_questions is None:
            sub_questions = self._line_fallback(content)

        # ---------------- LAYER 4: FINAL SAFETY ----------------
        sub_questions = self._final_fallback(sub_questions, user_query)

        return sub_questions

    # ==========================================================
    # 🔧 HELPERS
    # ==========================================================

    def _safe_json_parse(self, text):
        try:
            data = json.loads(text)

            if isinstance(data, dict):
                data = list(data.values())

            if isinstance(data, list):
                return data

        except:
            return None

        return None

    def _extract_json_array(self, text):
        match = re.search(r"\[.*?\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                return None
        return None

    def _line_fallback(self, text):
        lines = [
            line.strip("-•1234567890. ").strip()
            for line in text.split("\n")
            if line.strip()
        ]

        if len(lines) >= 4:
            return lines[:4]

        return None

    def _final_fallback(self, questions, user_query):
        # Ensure valid list
        if not isinstance(questions, list):
            questions = []

        # Clean + filter
        cleaned = []
        for q in questions:
            if isinstance(q, str) and len(q.strip()) > 5:
                cleaned.append(q.strip())

        # Ensure exactly 4
        if len(cleaned) < 4:
            fallback = [
                f"What is {user_query} and why is it important?",
                f"What are the key components or aspects of {user_query}?",
                f"What are the advantages and disadvantages of {user_query}?",
                f"What are the future implications or trends related to {user_query}?"
            ]

            cleaned.extend(fallback)

        return cleaned[:4]

