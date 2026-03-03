from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
prompt=input("Enter your prompt:")
response = client.chat.completions.create(
        model="qwen2.5-vl-3b-instruct",
        messages=[{"role": "user", "content": prompt}]
)

print(response.choices[0].message.content)
