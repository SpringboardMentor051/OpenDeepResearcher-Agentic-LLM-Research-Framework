import json
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

class PlannerAgent:

    def generate_subquestions(self, question):

        SYSTEM_PROMPT = f""" Break the question into 5 researchable sub questions.

Question:
{question}

Return only the numbered list.
"""

        response = client.chat.completions.create(
            model="qwen2.5-vl-3b-instruct",
            messages=[{"role":"user","content":SYSTEM_PROMPT}],
            temperature=1.0 ,
            max_tokens= 100,
            
        )

        text = response.choices[0].message.content

        sub_questions = [
        q.split(".",1)[-1].strip()
        for q in text.split("\n") if q.strip()
        ]

        return sub_questions


    def save_to_json(self, main_question, sub_questions):

        data = {
            "main_question": main_question,
            "sub_questions": []
        }

        for q in sub_questions:
            data["sub_questions"].append({
                "question": q,
                "answer": "",
                'url': ""
            })

        with open("research_data.json","w") as f:
            json.dump(data,f,indent=4)



if __name__ == "__main__":

    planner = PlannerAgent()

    # question = input("Enter research question:")

    sub_q = planner.generate_subquestions(question)
    # print(sub_q)
    planner.save_to_json(question, sub_q)

    # print("Sub questions saved to JSON")