from openai import OpenAI


client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

while True:
    prompt = input("Enter your prompt: ")

    response = client.chat.completions.create(
        model="qwen2.5-vl-7b-instruct",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    print("\nLLM Response:")
    print(response.choices[0].message.content)
    
    