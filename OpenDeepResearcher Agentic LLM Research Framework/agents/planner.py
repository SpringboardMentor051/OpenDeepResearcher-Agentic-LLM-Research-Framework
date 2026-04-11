from langchain_ollama import OllamaLLM
from halo import Halo


class PlannerAgent:
    def __init__(self):
        # Connect to local model running via Ollama
        self.llm = OllamaLLM(model="gemma:2b")

    def create_plan(self, topic: str):
        prompt = f"""
You are a research planning assistant.

Break the following research topic into 5 clear and structured sub-questions.

Topic: {topic}

Return the output as a numbered list.
"""

        response = self.llm.invoke(prompt)

        # Convert model output (string) into list of questions
        questions = response.split("\n")
        questions = [q.strip("1234567890. ").strip() for q in questions if q.strip()]

        return questions


# -------- TEST BLOCK --------

if __name__ == "__main__":

    planner = PlannerAgent()

    topic = input("Enter research topic: ")

    spinner = Halo(text="Generating research plan...", spinner="dots")
    spinner.start()

    plan = planner.create_plan(topic)

    spinner.stop()
    print("Research plan generated successfully.")

    print("\nResearch Plan:\n")

    for i, q in enumerate(plan, 1):
        print(f"{i}. {q}")