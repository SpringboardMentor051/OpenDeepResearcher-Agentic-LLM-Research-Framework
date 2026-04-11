from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()


class WriterAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=os.getenv("LM_STUDIO_URL"),
            api_key="lm-studio",
            model=os.getenv("MODEL_NAME"),
            temperature=0.3,
            max_tokens=2000
        )
        self.last_generated_report = ""

    def generate_initial_report(self, topic: str, context: str) -> str:
        prompt = f"""
### ROLE
You are a Senior Technical Researcher.

### TOPIC
{topic}

### DATA
{context}

### STRUCTURE
1. Title
2. Introduction (2 paragraphs)
3. Detailed Analysis (4 pillars)
4. Practical Examples
5. Conclusion

### RULES
- No bullet points
- No repetition
- Academic tone

Generate report:
"""
        try:
            result = self.llm.invoke(prompt)
            self.last_generated_report = result.content.strip()
            return self.last_generated_report
        except Exception as e:
            return f"Writer error: {str(e)}"

    def handle_follow_up(self, query: str, context: str) -> str:
        if not self.last_generated_report:
            return "Please generate a report first."

        prompt = f"""
You are a researcher.

REPORT:
{self.last_generated_report}

QUESTION:
{query}

Answer only the question in 2-3 paragraphs.
Do not rewrite full report.
"""
        try:
            result = self.llm.invoke(prompt)
            return result.content.strip()
        except Exception as e:
            return f"Follow-up error: {str(e)}"