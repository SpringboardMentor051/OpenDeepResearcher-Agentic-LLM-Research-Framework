from __future__ import annotations


PLANNER_SYSTEM_PROMPT = (
	"You are a research planning assistant. Break a topic into focused web-research "
	"sub-questions. Return only a JSON array of strings."
)

ANSWER_SYSTEM_PROMPT = (
	"You are a helpful research assistant. Answer the user's question using the supplied "
	"web search results. Provide a detailed, well-structured answer that is accurate and clear. "
	"If sources disagree, explain the disagreement and why it may exist. If evidence is weak, "
	"state what is uncertain and what additional evidence would improve confidence."
)

WRITER_SYSTEM_PROMPT = (
	"You are a concise research writer. Synthesize evidence into a structured summary "
	"with sections: Overview, Key Findings, and Gaps/Next Steps."
)


def build_planner_user_prompt(topic: str, max_questions: int) -> str:
	return (
		f"Topic: {topic}\n"
		f"Return {max_questions} or fewer sub-questions that are specific, non-overlapping, "
		"and answerable via web search."
	)


def build_answer_user_prompt(question: str, evidence: list[dict[str, str]]) -> str:
	evidence_lines: list[str] = []
	for index, item in enumerate(evidence, start=1):
		evidence_lines.append(
			f"{index}. {item['title']}\n"
			f"URL: {item['url']}\n"
			f"Summary: {item['content']}"
		)

	evidence_blob = "\n\n".join(evidence_lines)
	return (
		f"Question: {question}\n\n"
		f"Web results:\n{evidence_blob}\n\n"
		"Write a detailed answer using this structure:\n"
		"1) Direct Answer\n"
		"2) Key Details and Context\n"
		"3) Conflicting or Uncertain Points\n"
		"4) Practical Takeaways\n"
		"5) Sources Used (title plus URL list)\n\n"
		"Use the source evidence, avoid speculation, and keep claims tied to the provided web results."
	)


def build_writer_user_prompt(
	topic: str,
	subquestions: list[str],
	evidence_by_question: dict[str, list[dict[str, str]]],
) -> str:
	evidence_sections: list[str] = []
	for question in subquestions:
		evidence_sections.append(f"Sub-question: {question}")
		for item in evidence_by_question.get(question, []):
			evidence_sections.append(
				f"- {item['title']} ({item['url']}): {item['content']}"
			)

	evidence_blob = "\n".join(evidence_sections)
	return (
		f"Topic: {topic}\n\n"
		f"Sub-questions:\n" + "\n".join([f"- {q}" for q in subquestions]) + "\n\n"
		f"Evidence:\n{evidence_blob}\n\n"
		"Write a coherent synthesis that directly answers the sub-questions."
	)