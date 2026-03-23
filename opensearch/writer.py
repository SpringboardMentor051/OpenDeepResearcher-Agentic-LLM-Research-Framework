import os
from openai import OpenAI

class Writer:
    def __init__(self):
        # Updated to point to Ollama running locally in Colab
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "ollama"),
            base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1"),
        )
        # Updated to the Qwen model we pulled
        self.model = os.getenv("OPENAI_MODEL", "llama3")

    def summarize(self, topic: str, search_results: list[dict]) -> str:
        snippets = []
        for i, item in enumerate(search_results[:8], start=1):
            snippets.append(
                f"[{i}] {item.get('title', '')}\n"
                f"URL: {item.get('url', '')}\n"
                f"{item.get('content', '')}"
            )

        if not snippets:
            return "No data found to summarize."

        prompt = (
            f"Topic: {topic}\n\n"
            "Write a short research summary with:\n"
            "1) Summary\n2) Key points\n3) Sources\n\n"
            f"Evidence:\n{chr(10).join(snippets)}"
        )

        try:
            res = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=2500,
            )
            return res.choices[0].message.content or "No summary generated."
        except Exception as e:
            print(f"Writer Error: {e}")
            # Lightweight fallback if model is unavailable.
            lines = [f"Summary for: {topic}", "", "Key points:"]
            for item in search_results[:3]:
                # Grab the clean snippet, no length limit!
                text = item.get('content', 'No content available.')
                lines.append(f"- {item.get('title', 'Untitled')}: {text}")
            lines.append("")
            lines.append("Sources:")
            for item in search_results[:3]:
                if item.get("url"):
                    lines.append(f"- {item['url']}")
            return "\n".join(lines)