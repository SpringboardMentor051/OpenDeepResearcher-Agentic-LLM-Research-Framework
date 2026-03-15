from openai import OpenAI
from config.settings import LLM_URL, MODEL_NAME, LLM_API_KEY
from rag import get_research_rag

client = OpenAI(
    base_url=LLM_URL + "/v1",
    api_key=LLM_API_KEY
)


def writer_agent(topic: str, search_results: str, plan: str = "") -> dict:
    """
    Writer Agent: Synthesizes search results into a coherent, well-structured summary.
    Uses RAG to retrieve relevant context for enhanced generation.
    
    Args:
        topic: The research topic
        search_results: Content from search results to synthesize
        plan: The research plan (for context)
        
    Returns:
        dict with 'summary', 'key_points', and 'sources' keys
    """
    # Retrieve relevant context from RAG system
    rag_context = get_research_rag().get_context_for_topic(topic, plan, k=8)
    
    prompt = f"""You are an expert research synthesizer. Based on the following information, write a clear, comprehensive, and well-structured research report.

Topic: {topic}

Research Plan:
{plan}

Recent Search Results:
{search_results}

Relevant Context from Knowledge Base:
{rag_context}

Please provide the output formatted strictly as a 5-step research report containing the following sections:
1. Abstract (A concise summary of the research)
2. Introduction & Background (Context and relevance of the topic)
3. Methodology (How the research is approached based on the plan)
4. Key Findings & Discussion (The core synthesized information from results and historical context)
5. Conclusion & Limitations (Final thoughts and areas needing further research)

Write in an informative, objective academic style. When referencing information, distinguish between recent findings and established knowledge from the context."""
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )
    
    summary_text = response.choices[0].message.content
    
    # Parse key points (if present in response)
    key_points = []
    if "Key finding" in summary_text or "bullet" in summary_text.lower():
        lines = summary_text.split('\n')
        for line in lines:
            if line.strip().startswith('-') or line.strip().startswith('•'):
                key_points.append(line.strip()[1:].strip())
    
    return {
        "topic": topic,
        "summary": summary_text,
        "key_points": key_points,
        "word_count": len(summary_text.split())
    }