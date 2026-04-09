from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from .agents import PlannerAgent, SearcherAgent, WriterAgent


class ResearchState(TypedDict, total=False):
    topic: str
    subquestions: list[str]
    evidence_by_question: dict[str, list[dict[str, str]]]
    evidence: list[dict[str, str]]
    draft: str


@dataclass
class ResearchFlow:
    planner: PlannerAgent
    searcher: SearcherAgent
    writer: WriterAgent

    def __post_init__(self) -> None:
        self._graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(ResearchState)
        graph.add_node("planner", self._planner_node)
        graph.add_node("searcher", self._searcher_node)
        graph.add_node("writer", self._writer_node)

        graph.add_edge(START, "planner")
        graph.add_edge("planner", "searcher")
        graph.add_edge("searcher", "writer")
        graph.add_edge("writer", END)
        return graph.compile()

    def _planner_node(self, state: ResearchState) -> dict[str, Any]:
        topic = state["topic"]
        subquestions = self.planner.plan(topic)
        return {"subquestions": subquestions}

    def _searcher_node(self, state: ResearchState) -> dict[str, Any]:
        subquestions = state.get("subquestions", [])
        evidence_by_question = self.searcher.gather(subquestions)
        flattened: list[dict[str, str]] = []
        for question, items in evidence_by_question.items():
            for item in items:
                flattened.append(
                    {
                        "subquestion": question,
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("content", ""),
                    }
                )
        return {
            "evidence_by_question": evidence_by_question,
            "evidence": flattened,
        }

    def _writer_node(self, state: ResearchState) -> dict[str, Any]:
        topic = state["topic"]
        subquestions = state.get("subquestions", [])
        evidence_by_question = state.get("evidence_by_question", {})
        draft = self.writer.write(topic, subquestions, evidence_by_question)
        return {"draft": draft}

    def run(self, topic: str) -> dict[str, Any]:
        final_state: ResearchState = self._graph.invoke({"topic": topic})

        return {
            "topic": topic,
            "subquestions": final_state.get("subquestions", []),
            "plan": final_state.get("subquestions", []),
            "evidence": final_state.get("evidence", []),
            "evidence_by_question": final_state.get("evidence_by_question", {}),
            "draft": final_state.get("draft", ""),
        }
