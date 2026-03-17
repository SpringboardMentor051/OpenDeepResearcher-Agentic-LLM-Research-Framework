from openai import OpenAI
import json

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

class WriterAgent:

    def summarize(self, content):

        prompt = f"""
You are an expert research assistant.

Summarize the following research content clearly and concisely.

Instructions:
- Extract only key facts
- Remove repetition
- Write a clean explanation
- Keep it between 120–180 words

Content:
{content}
"""

        response = client.chat.completions.create(
            model="qwen2.5-vl-3b-instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3,
            top_p=0.9
        )

        return response.choices[0].message.content.strip()


    def write_answers(self, file_path="research_data.json"):

        with open(file_path, "r") as f:
            data = json.load(f)

        for i, item in enumerate(data["sub_questions"]):

            content = item["answer"]   # researcher stored raw content here

            print(f"Summarizing Sub Question {i+1}...")

            summary = self.summarize(content)

            data["sub_questions"][i]["answer"] = summary

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        # print("Summaries saved to JSON")