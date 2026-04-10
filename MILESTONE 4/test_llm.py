from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="not-needed"
)

def ask_llm(question):
    response = client.chat.completions.create(
        model="qwen2.5-coder-7b-instruct",   # ⚠️ Must match EXACT model name in LM Studio
        messages=[
            {"role": "user", "content": question}
        ]
    )

    return response.choices[0].message.content

print(ask_llm("Hello! Are you working?"))