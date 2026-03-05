from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
llm = ChatOpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio",
    model="qwen2.5-vl-7b-instruct",
)

def stub_research_flow(topic: str):
    print(f"\n Researching Topic: {topic}\n")

    
    plan_prompt = f"Break down this research topic into 3 sub-questions: {topic}"
    plan = llm.invoke(plan_prompt)
    print("Research Plan:\n", plan.content)

    
    write_prompt = f"Write a brief summary paragraph about: {topic}"
    summary = llm.invoke(write_prompt)
    print("\nSummary:\n", summary.content)

    print("\n Pipeline complete!")

if __name__ == "__main__":
    stub_research_flow("The impact of AI on Infrastructure")