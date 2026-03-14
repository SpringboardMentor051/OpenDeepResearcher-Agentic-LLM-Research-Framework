import warnings
warnings.filterwarnings("ignore")
from agent.planner import plan_query
from agent.searcher import search_web
from agent.writer import generate_answer


def main():
    topic = input("Enter your research topic: ").strip()

    if not topic:
        print("Please enter a valid topic.")
        return

    print("\n Planning research...")
    plan = plan_query(topic)

    questions = plan.get("questions", [topic])
    print(f"Generated Questions: {questions}")

    print("\n Searching with Tavily...")
    full_context = ""

    for question in questions:
        print(f"Searching: {question}")
        results = search_web(question)
        full_context += results + "\n\n"

    if not full_context.strip():
        print("No search results found.")
        return

    print("\n Generating final answer with LM Studio...")
    answer = generate_answer(topic, full_context)

    print("\n Final Answer:\n")
    print(answer)

    print("\nPipeline complete!")


if __name__ == "__main__":
    main()
