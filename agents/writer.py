import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()


class Writer:
    def __init__(self):
       self.llm = ChatOpenAI(
    base_url=os.getenv("LM_STUDIO_BASE_URL", "http://127.0.0.1:1234") + "/v1",
    api_key="lm-studio",
    model=os.getenv("LM_STUDIO_MODEL", "qwen2.5-7b-instruct"),
    temperature=0.4,
)

    def summarize(self, topic: str, results: list[dict], history_context: str = "") -> str:
        try:
            formatted = ""
            for i, r in enumerate(results[:5], 1):  # ✅ limit results
                formatted += f"\n[Source {i}]\n{r.get('content','')}\n"

            prompt = f"""
            Write a clear research summary about: {topic}
            Use these sources:
            {formatted}
            """

            resp = self.llm.invoke([HumanMessage(content=prompt)])
            return resp.content

        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def generate_full_report(self, topic, queries, results, summary):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        report = f"# {topic}\n\n## Summary\n{summary}\n\n## Queries\n"
        for q in queries:
            report += f"- {q}\n"

        return report