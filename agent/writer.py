from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("LM_STUDIO_URL"),
    api_key="lm-studio",
    model=os.getenv("MODEL_NAME")
)

def write_response(query: str) -> str:
    prompt = f"Write a detailed summary paragraph about: {query}"
    result = llm.invoke(prompt)
    print("\nSummary:\n", result.content)
    return result.content