import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()


class Planner:
    def __init__(self):
        self.llm = ChatOpenAI(
    base_url=os.getenv("LM_STUDIO_BASE_URL", "http://127.0.0.1:1234") + "/v1",
    api_key="lm-studio",
    model=os.getenv("LM_STUDIO_MODEL", "qwen2.5-7b-instruct"),
    temperature=0.3,
)
          
        

    def plan(self, topic: str, history_context: str = "") -> list[str]:
        try:
            ctx = f"\nConversation so far:\n{history_context}\n" if history_context else ""
            prompt = (
                f"You are a research planner.{ctx}\n"
                f"Break this research topic into exactly 5 short search queries.\n"
                f"Return ONLY a numbered list.\n\n"
                f"Topic: {topic}"
            )

            resp = self.llm.invoke([HumanMessage(content=prompt)])
            lines = [l.strip() for l in resp.content.split("\n") if l.strip()]
            return [l.lstrip("0123456789.-) ").strip() for l in lines][:5]

        except Exception as e:
            return ["basic research query", "topic overview", "latest trends", "applications", "future scope"]