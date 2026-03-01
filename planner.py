from openai import OpenAI
import json

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

SYSTEM_PROMPT = """
You are a professional Research Planner Agent.

Your job:
1. Break the user's problem into logical sub-questions.
2. Create a structured research roadmap.
3. Identify required knowledge areas.
4. Provide execution order.

Always respond strictly in JSON format:

{
  "main_question": "",
  "sub_questions": [],
  "research_plan": [],
  "required_knowledge": [],
  "execution_order": []
}
Do not add explanations outside JSON.
"""

def chat_planner():
    messages = [
        {"role": "system", "content":  SYSTEM_PROMPT}
    ]

    print("Planner Agent Ready (type 'exit' to quit)\n")

    while True:
        user_input = input("User: ")

        if user_input.lower() == "exit":
            break

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="qwen2.5-vl-3b-instruct", # using qwen 2.5-vl-3b-instruct model due to hardware constrain's
            messages=messages,
            temperature=0.3
        )

        reply = response.choices[0].message.content

        print("\nPlanner Agent:\n")
        print(reply)
        print("\n" + "-"*50 + "\n")

        messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    chat_planner()