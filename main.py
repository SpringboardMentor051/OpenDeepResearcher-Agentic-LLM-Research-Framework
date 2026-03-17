from planner import PlannerAgent
from researcher import ResearcherAgent
from writer import WriterAgent
import json

planner = PlannerAgent()
researcher = ResearcherAgent()
writer = WriterAgent()

question = input("Enter research question: ")

sub_questions = planner.generate_subquestions(question)

planner.save_to_json(question, sub_questions)

raw_answers, urls = researcher.research(sub_questions)

researcher.save_answers_to_json(raw_answers, urls)

writer.write_answers()


with open("research_data.json", "r") as f:
    data = json.load(f)

print("\nMAIN QUESTION:")
print(data["main_question"])

print("\nSUB QUESTIONS, ANSWERS AND SOURCES\n")

for i, item in enumerate(data["sub_questions"], start=1):

    question = item.get("question", "No Question")
    answer = item.get("answer", "No Answer")
    urls = item.get("url", "")

    print(f"\nSub Question {i} : {question}\n")

    print("Answer:\n")
    print(answer)

    print("\nSources:\n")

    for u in urls.split("\n"):
        print(u)

    print("\n" + "=" * 150)