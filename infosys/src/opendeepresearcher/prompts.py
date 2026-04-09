from __future__ import annotations


PLANNER_SYSTEM_PROMPT = (
	"You are an expert research planner. Break the user topic into focused, non-overlapping "
	"sub-questions that can be answered with reliable web sources. Prioritize questions that "
	"improve decision quality and factual confidence. Return only a JSON array of strings. "
	"Do not include markdown, commentary, or keys."
)

ANSWER_SYSTEM_PROMPT = (
	"You are ChatGPT-style research assistant writing a final answer. Use only the provided "
	"web evidence. Keep the response clear, direct, practical, and factually grounded. "
	"If evidence is weak or missing, state that explicitly instead of guessing. "
	"If sources conflict, explain the disagreement and likely reason. "
	"Do not ask the user follow-up questions. Do not include process notes or self-talk. "
	"Be transparent about confidence and limitations."
)

WRITER_SYSTEM_PROMPT = (
	"You are a senior research writer producing a polished ChatGPT-style result. "
	"Synthesize multiple evidence snippets into one coherent, reader-friendly report. "
	"Write with concise-first clarity, then depth. Tie claims to evidence, highlight uncertainty "
	"honestly, avoid filler, and do not end with follow-up questions."
)


def build_planner_user_prompt(topic: str, max_questions: int) -> str:
	return (
		f"Topic: {topic}\n"
		f"Return {max_questions} or fewer sub-questions that are specific, non-overlapping, "
		"and answerable via web search. Prefer sub-questions that cover: "
		"(1) key facts, (2) current developments, (3) trade-offs/risks, and "
		"(4) practical implications. Return JSON array only."
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
		"Write a helpful answer in markdown using this exact section order:\n"
		"1) Direct Answer (2-5 sentences)\n"
		"2) What the Evidence Says\n"
		"3) Key Takeaways\n"
		"4) Conclusion\n"
		"5) Sources\n\n"
		"Rules:\n"
		"- Keep claims tied to the provided evidence only.\n"
		"- No speculation or invented facts.\n"
		"- Sound like a finalized ChatGPT answer, not a brainstorming draft.\n"
		"- Do not ask the user follow-up questions.\n"
		"- Mention confidence level (High/Medium/Low) with a short reason.\n"
		"- In Sources, list each item as: - Title - URL"
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
		"Write a coherent markdown synthesis that directly answers the sub-questions using this "
		"section order:\n"
		"1) Executive Summary\n"
		"2) Key Findings by Sub-question\n"
		"3) Cross-Cutting Insights\n"
		"4) Risks, Gaps, and Open Questions\n"
		"5) Recommended Next Actions\n"
		"6) Sources\n\n"
		"Rules:\n"
		"- Keep tone natural and concise, like a strong ChatGPT research response.\n"
		"- Tie important claims to source evidence.\n"
		"- If evidence is weak or conflicting, say that explicitly.\n"
		"- Do not include follow-up questions at the end.\n"
		"- In Sources, provide bullet items as: - Title - URL"
	)