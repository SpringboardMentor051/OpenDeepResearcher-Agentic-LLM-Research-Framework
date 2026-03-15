from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

print("Expert AI Research Assistant Ready (type 'exit' to quit)\n")

while True:

    prompt = input("Enter your research question: ")

    if prompt.lower() == "exit":
        break

    print("\nAnalyzing...\n")

    response = client.chat.completions.create(
        model="qwen2.5-vl-7b-instruct",
        messages=[
            {
                "role": "system",
                "content": """
You are an expert AI researcher and analyst.

When answering:
- Think like a research expert.
- Provide clear explanations.
- Highlight key insights.
- Use structured sections.
- End with a short summary.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.6
    )

    print("AI Research Response:\n")
    print(response.choices[0].message.content)
    print("\n")