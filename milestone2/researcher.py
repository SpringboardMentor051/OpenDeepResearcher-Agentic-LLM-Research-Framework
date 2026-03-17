import json
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

class ResearcherAgent:

    def research(self, sub_questions):

        answers = []
        urls = []

        for question in sub_questions:

            # print("Researching:", question)

            response = client.search(
                query=question,
                search_depth="advanced",
                max_results=2,
                include_answer=True,
                include_raw_content=False,
                
            )

            results = response.get("results", [])
            # print(results)   # FIXED

            answer = ""
            url = ""

            for r in results:
                answer += r.get("content", "") + "\n"
                url += r.get("url", "") + "\n"

            answers.append(answer.strip())
            urls.append(url.strip())

        return answers, urls


    def save_answers_to_json(self, answers,urls, file_path="research_data.json"):

        with open(file_path, "r") as f:
            data = json.load(f)

        sub_questions = data["sub_questions"]

        for i in range(len(sub_questions)):

            if i < len(answers):
                sub_questions[i]["answer"] = answers[i]
                sub_questions[i]['url'] = urls[i]

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        # print("Answers saved successfully to JSON")


if __name__ == "__main__":

    researcher = ResearcherAgent()

    # sub_questions = [
    #     "What is Artificial Intelligence?",
    #     "What are the applications of AI?"
    # ]

    answers,urls  = researcher.research(sub_questions)
    # print(urls)
    researcher.save_answers_to_json(answers,urls)