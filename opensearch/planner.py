from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

def plan_research(topic):

    print("\nPlanner Agent analyzing topic...\n")

    response = client.chat.completions.create(
        model="qwen2.5-vl-7b-instruct",
        messages=[
            {"role": "system", "content": "You are an expert AI research planner."},
            {"role": "user", "content": f"""
Break the following topic into exactly 5 research questions.

Topic: {topic}
Return only the questions.
"""}
        ],
        temperature=0.6
    )

    questions = response.choices[0].message.content.split("\n")

    return questions










