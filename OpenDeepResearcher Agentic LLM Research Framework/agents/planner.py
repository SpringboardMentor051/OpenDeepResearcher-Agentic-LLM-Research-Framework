from langchain_community.llms import Ollama


class PlannerAgent:
    def __init__(self):
        self.llm = Ollama(model="gemma:2b")

    def create_plan(self, topic: str):
        prompt = f"""
You are a research planning assistant.

Break the following research topic into 5 clear and structured sub-questions.

Topic: {topic}

Return the output as a numbered list.
"""
        response = self.llm.invoke(prompt)
        return response