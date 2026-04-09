# Architecture (Phase 2)

## Agent Pipeline

The system is orchestrated using `LangGraph` with a linear state graph:

1. **Planner node**
   - Input: `topic`
   - Output: `subquestions` (focused, web-searchable)
2. **Searcher node**
   - Input: `subquestions`
   - Output: `evidence_by_question` and flattened `evidence`
3. **Writer node**
   - Input: `topic`, `subquestions`, `evidence_by_question`
   - Output: `draft` summary with clear structure

## State Contract

`ResearchState` fields passed across the graph:
- `topic: str`
- `subquestions: list[str]`
- `evidence_by_question: dict[str, list[dict[str, str]]]`
- `evidence: list[dict[str, str]]`
- `draft: str`

## Runtime Behavior

- Planner uses the configured LLM to produce sub-questions.
- Searcher queries Tavily once per sub-question.
- Writer synthesizes all gathered evidence into a final summary.
- `main.py` returns JSON payload and writes to `results/latest.json` by default.
