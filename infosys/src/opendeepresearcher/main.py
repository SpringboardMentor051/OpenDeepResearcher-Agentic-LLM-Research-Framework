from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agents import PlannerAgent, SearcherAgent, WriterAgent
from .config import get_settings
from .flow import ResearchFlow
from .llm import LLMClient
from .prompts import ANSWER_SYSTEM_PROMPT, build_answer_user_prompt
from .search import TavilyClient


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="Run OpenDeepResearcher flow")
	parser.add_argument("topic", nargs="?", help="Research topic")
	parser.add_argument(
		"--ask",
		dest="question",
		help="Search the web with Tavily and print an LLM summary of the results",
	)
	parser.add_argument(
		"--chat",
		action="store_true",
		help="Start interactive chat that searches the web first, then summarizes with the LLM",
	)
	parser.add_argument(
		"--output",
		default="results/latest.json",
		help="Output JSON path (default: results/latest.json)",
	)
	return parser


def run(topic: str) -> dict:
	settings = get_settings()
	llm = LLMClient(settings=settings)
	search = TavilyClient(settings=settings)
	flow = ResearchFlow(
		planner=PlannerAgent(llm=llm),
		searcher=SearcherAgent(search=search),
		writer=WriterAgent(llm=llm),
	)
	return flow.run(topic)


def ask(question: str) -> str:
	settings = get_settings()
	llm = LLMClient(settings=settings)
	search = TavilyClient(settings=settings)
	evidence = search.search(question, max_results=5)
	return llm.generate(
		system_prompt=ANSWER_SYSTEM_PROMPT,
		user_prompt=build_answer_user_prompt(question, evidence),
	)


def chat() -> None:
	print("Chat mode started. Each question is searched on the web, then summarized by the LLM. Type 'exit' or 'quit' to end.")
	while True:
		try:
			question = input("You: ").strip()
		except (EOFError, KeyboardInterrupt):
			print()
			break

		if not question:
			continue

		if question.lower() in {"exit", "quit"}:
			break

		answer = ask(question)
		print(f"Assistant: {answer}\n")


def main() -> None:
	parser = build_parser()
	args = parser.parse_args()
	if args.chat:
		chat()
		return

	if args.question:
		print(ask(args.question))
		return

	if not args.topic:
		parser.error("Provide a research topic, use --ask \"your question\", or start --chat.")

	result = run(args.topic)

	output_path = Path(args.output)
	output_path.parent.mkdir(parents=True, exist_ok=True)
	output_json = json.dumps(result, ensure_ascii=False, indent=2)
	output_path.write_text(output_json, encoding="utf-8")

	print(output_json)


if __name__ == "__main__":
	main()
