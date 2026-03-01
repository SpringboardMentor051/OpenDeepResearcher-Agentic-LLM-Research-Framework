from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

def plan_research(topic):
    response = client.chat.completions.create(
        model="qwen2.5-vl-7b-instruct",
        messages=[
            {"role": "system", "content": "You are a research planner."},
            {"role": "user", "content": f"Break this topic into sub-questions: {topic}"}
        ]
    )
    
    return response.choices[0].message.content


if __name__ == "__main__":
    topic = input("Enter research topic: ")
    result = plan_research(topic)
    print("\nResearch Plan:\n")
    print(result)