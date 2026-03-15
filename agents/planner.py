from openai import OpenAI
from config.settings import LLM_URL, MODEL_NAME, LLM_API_KEY

client = OpenAI(
    base_url=LLM_URL + "/v1",
    api_key=LLM_API_KEY
)


def planner_agent(topic: str) -> dict:
    """
    Planner Agent: Breaks down the research topic into structured planning steps.
    
    Args:
        topic: The research topic to plan for
        
    Returns:
        dict with 'topic', 'steps', and 'plan' keys
    """
    prompt = f"""You are a research planning expert. Break down the following research topic into 5 detailed, actionable research steps.

Topic: {topic}

Provide your response as a numbered list with clear, specific steps that a researcher should follow."""
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000
    )
    
    plan_text = response.choices[0].message.content
    
    return {
        "topic": topic,
        "plan": plan_text,
        "steps": plan_text.split('\n')  # Split into individual steps
    }