from utils.llm import get_llm

llm = get_llm()

def writer_agent(research_data):

    prompt = f"""
You are a research writer.

Create report in this structure ONLY:

{{
 "title": "",
 "introduction": "",
 "sections": [
   {{
     "heading": "",
     "summary": ""
   }}
 ],
 "conclusion": ""
}}

Use this research data:

{research_data}
"""

    response = llm.invoke(prompt)

    return response.content