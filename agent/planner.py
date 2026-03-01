from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("LM_STUDIO_URL"),
    api_key="lm-studio",
    model=os.getenv("MODEL_NAME")
)

def plan_query(query: str) -> str:
    prompt = f"Break down this research topic into 3 sub-questions: {query}"
    result = llm.invoke(prompt)
    print("Research Plan:\n", result.content)
    return result.content