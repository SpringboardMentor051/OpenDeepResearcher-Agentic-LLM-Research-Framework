import json
import os

from openai import OpenAI


class Planner:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "lm-studio"),
            base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:1234/v1"),
        )
        self.model = os.getenv("OPENAI_MODEL", "qwen/qwen3.5-9b")

    def plan(self, topic: str) -> list[str]:
        """Break one topic into 3-4 focused web-search queries."""
        system = (
            "Return only JSON in this format: "
            '{"queries":["q1","q2","q3"]}. Keep queries short.'
        )
        try:
            res = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"Topic: {topic}"},
                ],
                temperature=0.2,
                max_tokens=200,
            )
            content = res.choices[0].message.content or ""
            queries = json.loads(content).get("queries", [])
            queries = [q.strip() for q in queries if isinstance(q, str) and q.strip()]
            if queries:
                return queries[:4]
        except Exception:
            pass

        return [
            f"{topic} overview",
            f"{topic} latest trends",
            f"{topic} key challenges",
            f"{topic} real-world applications",
        ]