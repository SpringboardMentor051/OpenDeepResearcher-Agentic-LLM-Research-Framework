from milestone2.utils.llm import get_llm

llm = get_llm()

def writer_agent(research_data):

    prompt = f"""
You are a helpful AI assistant.

Write a clean, human-readable report.

Do NOT return JSON.
Do NOT use dictionary format.

Write like ChatGPT:
- Proper paragraphs
- Clear headings
- Simple explanation

Data:
{research_data}

Generate a well-structured explanation.
"""

    response = llm.invoke(prompt)

    return response.content