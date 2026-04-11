from langchain_ollama import OllamaLLM


class WriterAgent:
    def __init__(self):
        # Keep model light for speed
        self.llm = OllamaLLM(model="gemma:2b")

    def write_report(self, topic: str, research_dict: dict):

        # -----------------------------
        # Collect and clean data
        # -----------------------------
        all_data = []
        sources = []

        for question, results in research_dict.items():
            for r in results:

                if not r.get("content") or not r.get("url"):
                    continue

                all_data.append({
                    "question": question,
                    "title": r.get("title", ""),
                    "content": r.get("content", ""),
                    "url": r.get("url", "")
                })

                sources.append(f"- {r['title']} : {r['url']}")

        # remove duplicate sources
        sources = list(dict.fromkeys(sources))

        # -----------------------------
        # Handle empty case
        # -----------------------------
        if not all_data:
            return f"""
# Research Report: {topic}

## Abstract
No sufficient research data was retrieved from sources.

## Conclusion
Unable to generate a detailed report due to lack of data.
"""

        # -----------------------------
        # Limit data for speed (IMPORTANT)
        # -----------------------------
        context = ""
        for item in all_data[:8]:   # speed optimization
            context += f"""
Q: {item['question']}
Title: {item['title']}
Content: {item['content']}
Source: {item['url']}
"""

        # -----------------------------
        # Professional research prompt
        # -----------------------------
        prompt = f"""
You are an expert research analyst.

Write a professional research report.

Topic: {topic}

Follow this structure strictly:

1. Abstract
2. Introduction
3. Literature Review
4. Key Findings
5. Discussion
6. Applications
7. Conclusion

Rules:
- Use ONLY provided data
- Do NOT hallucinate
- Keep it structured and formal

DATA:
{context}
"""

        # -----------------------------
        # SINGLE LLM CALL (FAST)
        # -----------------------------
        response = self.llm.invoke(prompt)

        # -----------------------------
        # Final output
        # -----------------------------
        final_report = f"""
{response}

---

## References
{chr(10).join(sources[:6])}
"""

        return final_report


# -----------------------------
# LOCAL TEST (OPTIONAL)
# -----------------------------
if __name__ == "__main__":

    from planner import PlannerAgent
    from searcher import SearcherAgent

    topic = input("Enter research topic: ")

    planner = PlannerAgent()
    searcher = SearcherAgent()

    questions = planner.create_plan(topic)

    print("\nResearch Questions:")
    for q in questions:
        print("-", q)

    research_data = {}

    for q in questions:
        print(f"\nSearching: {q}")
        research_data[q] = searcher.search(q)

    writer = WriterAgent()

    print("\nGenerating report...\n")
    report = writer.write_report(topic, research_data)

    print(report)