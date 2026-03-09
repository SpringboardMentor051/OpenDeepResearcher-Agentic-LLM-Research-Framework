import os

from openai import OpenAI


class Writer:
	def __init__(self):
		self.client = OpenAI(
			api_key=os.getenv("OPENAI_API_KEY", "lm-studio"),
			base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:1234/v1"),
		)
		self.model = os.getenv("OPENAI_MODEL", "qwen/qwen3.5-9b")

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
				max_tokens=600,
			)
			return res.choices[0].message.content or "No summary generated."
		except Exception:
			# Lightweight fallback if model is unavailable.
			lines = [f"Summary for: {topic}", "", "Key points:"]
			for item in search_results[:3]:
				lines.append(f"- {item.get('title', 'Untitled')}: {item.get('content', '')[:180]}")
			lines.append("")
			lines.append("Sources:")
			for item in search_results[:3]:
				if item.get("url"):
					lines.append(f"- {item['url']}")
			return "\n".join(lines)
