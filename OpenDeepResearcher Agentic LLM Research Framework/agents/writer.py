from langchain_ollama import OllamaLLM
from halo import Halo

# Import other agents
#from planner import PlannerAgent
#from searcher import SearcherAgent 


class WriterAgent:
    def __init__(self):
        self.llm = OllamaLLM(model="gemma:2b")

    def write_report(self, topic: str, research_dict: dict):

        research_content = ""
        sources = []
        source_count = 0
        max_sources = 5
        # 🔵 Terminal color codes
        BLUE = "\033[94m"
        RESET = "\033[0m"
        BOLD = "\033[1m"

        # Convert research dictionary into context
        for question, results in research_dict.items():

            research_content += f"\nResearch Question: {question}\n"

            for r in results:

                if source_count >= max_sources:
                    break

                research_content += f"""
Title: {r['title']}
Content: {r['content']}
Source: {r['url']}
"""

                sources.append(
                    f"{BOLD}{r['title']}{RESET} : {BLUE}{r['url']}{RESET}"
                )

                source_count += 1

        # Prompt
        prompt = f"""
You are an expert research writer.

Write a well-structured research report using ONLY the research information below.

Topic: {topic}

Research Information:
{research_content}

Structure the report using these sections:

Introduction
Explain the topic clearly.

Key Concepts
Explain the main ideas and concepts.

Applications / Importance
Explain real-world uses or importance.

Conclusion
Provide a short summary of the topic.
"""

        response = self.llm.invoke(prompt)

        # Attach sources after report
        sources_text = "\n".join(sources)

        final_report = f"""
{response}

Sources
{sources_text}
"""

        return final_report


# -------- RUN INDIVIDUALLY FOR TESTING --------

if __name__ == "__main__":

    topic = input("Enter research topic: ")

    planner = PlannerAgent()
    searcher = SearcherAgent()
    writer = WriterAgent()

    # Generate research questions
    spinner = Halo(text="Generating research questions...", spinner="dots")
    spinner.start()
    questions = planner.create_plan(topic)
    spinner.stop()

    print("\nResearch Questions:")
    for q in questions:
        print("-", q)

    research_data = {}

    # Search information
    for q in questions:

        spinner = Halo(text=f"Searching: {q}", spinner="dots")
        spinner.start()

        results = searcher.search(q)

        spinner.stop()

        research_data[q] = results

    # Generate report
    spinner = Halo(text="Writing research report...", spinner="dots")
    spinner.start()

    report = writer.write_report(topic, research_data)

    spinner.stop()

    print("\n========== FINAL RESEARCH REPORT ==========\n")
    print(report)