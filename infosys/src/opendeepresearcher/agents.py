from __future__ import annotations

from dataclasses import dataclass
import json
import re

from .llm import LLMClient
from .prompts import (
    PLANNER_SYSTEM_PROMPT,
    WRITER_SYSTEM_PROMPT,
    build_planner_user_prompt,
    build_writer_user_prompt,
)
from .search import TavilyClient


@dataclass
class PlannerAgent:
    llm: LLMClient

    def plan(self, topic: str, max_questions: int = 5) -> list[str]:
        response = self.llm.generate(
            system_prompt=PLANNER_SYSTEM_PROMPT,
            user_prompt=build_planner_user_prompt(topic, max_questions),
        )
        questions = self._parse_subquestions(response)
        return questions[:max_questions] if questions else [f"What are the key facts about {topic}?"]

    def _parse_subquestions(self, text: str) -> list[str]:
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                cleaned = [str(item).strip() for item in parsed if str(item).strip()]
                if cleaned:
                    return cleaned
        except Exception:
            pass

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned_lines: list[str] = []
        for line in lines:
            line = re.sub(r"^[-*•]\s*", "", line)
            line = re.sub(r"^\d+[.)]\s*", "", line)
            if line:
                cleaned_lines.append(line)

        return cleaned_lines


@dataclass
class SearcherAgent:
    search: TavilyClient

    def gather(
        self,
        subquestions: list[str],
        max_results_per_question: int = 3,
    ) -> dict[str, list[dict[str, str]]]:
        evidence_by_question: dict[str, list[dict[str, str]]] = {}
        for question in subquestions:
            evidence_by_question[question] = self.search.search(
                question,
                max_results=max_results_per_question,
            )
        return evidence_by_question


@dataclass
class WriterAgent:
    llm: LLMClient

    def write(
        self,
        topic: str,
        subquestions: list[str],
        evidence_by_question: dict[str, list[dict[str, str]]],
    ) -> str:
        return self.llm.generate(
            system_prompt=WRITER_SYSTEM_PROMPT,
            user_prompt=build_writer_user_prompt(topic, subquestions, evidence_by_question),
        )
