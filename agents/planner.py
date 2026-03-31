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
You are an expert research planner.

Your task is to break the user's query into EXACTLY 4 high-quality research questions.

User Query:
{user_query}

INSTRUCTIONS:
- Understand the intent deeply
- If query is broad → cover different dimensions
- If query is specific → break into deeper aspects
- Avoid repetition
- Avoid generic questions

STRICT OUTPUT RULE:
Return ONLY a valid JSON list of 4 strings.

Example:
["Question 1", "Question 2", "Question 3", "Question 4"]
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

