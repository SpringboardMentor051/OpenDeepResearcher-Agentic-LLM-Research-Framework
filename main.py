import argparse
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from opensearch.planner import Planner
from opensearch.searcher import Searcher
from opensearch.writer import Writer

load_dotenv()


class ResearchState(TypedDict, total=False):
	topic: str
	plan: list[str]
	results: list[dict]
	summary: str


planner = Planner()
searcher = Searcher()
writer = Writer()


def planner_node(state: ResearchState) -> ResearchState:
	return {"plan": planner.plan(state["topic"])}


def searcher_node(state: ResearchState) -> ResearchState:
	return {"results": searcher.search_many(state.get("plan", []))}


def writer_node(state: ResearchState) -> ResearchState:
	return {"summary": writer.summarize(state["topic"], state.get("results", []))}


def build_app():
	graph = StateGraph(ResearchState)
	graph.add_node("planner", planner_node)
	graph.add_node("searcher", searcher_node)
	graph.add_node("writer", writer_node)
	graph.add_edge(START, "planner")
	graph.add_edge("planner", "searcher")
	graph.add_edge("searcher", "writer")
	graph.add_edge("writer", END)
	return graph.compile()


def run(topic: str) -> ResearchState:
	app = build_app()
	return app.invoke({"topic": topic})


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("topic", nargs="?", default="")
	parser.add_argument("--validate", action="store_true")
	args = parser.parse_args()

	topic = args.topic or ""
	if args.validate and not topic:
		topic = "Impact of small language models in edge AI"

	if not topic:
		topic = input("Enter your research question: ").strip()

	if not topic:
		raise SystemExit("No question provided.")

	output = run(topic)

	print("\nTopic:", topic)
	print("\nPlan:")
	for q in output.get("plan", []):
		print("-", q)
	print("\nSummary:\n")
	print(output.get("summary", "No summary generated."))