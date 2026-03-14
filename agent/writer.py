from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()


llm = ChatOpenAI(
    base_url=os.getenv("LM_STUDIO_URL"),
    api_key="lm-studio",
    model=os.getenv("MODEL_NAME"),
    temperature=0.3,
    max_tokens=2000
)


def generate_answer(topic: str, context: str) -> str:
    """
    Writer Agent
    Converts Tavily research context into a final answer.
    """

    if not context.strip():
        return "No research data found."

    prompt = f"""
    You are a professional research writer.

    TASK:
    Write a detailed, long-form report using the research information provided.
    Use well-structured paragraphs and full explanations.
    Do not invent any information.
    More like pragraphs than bullet points.
    TARGET LENGTH:
    Approximately 1200-1500 words (~2000 tokens).
    Expand on every point in the research data.

    TOPIC:
    {topic}

    RESEARCH DATA:
    {context}


    INSTRUCTIONS:
    - Use only the research data provided
    - Write clearly and logically
    - Provide a complete answer
    - Avoid bullet points, lists, or summaries
    """

    try:
        result = llm.invoke(prompt)
        return result.content.strip()

    except Exception as e:
        return f"Writer error: {str(e)}"