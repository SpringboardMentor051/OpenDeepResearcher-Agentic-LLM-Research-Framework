from openai import OpenAI
from dotenv import load_dotenv
from os import getenv

load_dotenv()


class Writer:
    def __init__(self, model_name: str, base_url: str):
        self.client = OpenAI(base_url=base_url, api_key=getenv("API_KEY"))
        self.model = model_name

    def summarize(
        self,
        sub_question: str,
        search_content: str,
        history: list,
        is_followup: bool = False,
        final: bool = False
    ) -> str:
        # Build a focused history summary — only extract relevant Q&A pairs
        history_summary = self._build_history_summary(history)

        if final and not is_followup:
            prompt = self._final_prompt(sub_question, search_content, history_summary)
        elif final and is_followup:
            prompt = self._followup_final_prompt(sub_question, search_content, history_summary)
        else:
            prompt = self._partial_prompt(sub_question, search_content, history_summary)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional research writer. Write structured, paragraph-based reports."},
                    {"role": "user", "content": prompt}
                ],
                timeout=60
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[Writer error: {e}]"

    def _build_history_summary(self, history: list) -> str:
        """Extract last 3 Q&A turns with truncated content."""
        recent = history[-6:]
        parts = []
        for msg in recent:
            role = msg["role"]
            content = msg["content"][:400]
            parts.append(f"{role.upper()}: {content}")
        return "\n".join(parts) if parts else "No prior conversation."

    def _final_prompt(self, query, content, history_summary):
        return f"""
You are an advanced research writer.

CONVERSATION CONTEXT:
{history_summary}

MAIN QUERY:
{query}

COLLECTED RESEARCH:
{content}

Write a comprehensive, professional research report answering the query.

FORMAT:
# [Descriptive Title]

## Introduction
Introduce the topic clearly in 2-3 sentences.

## Key Insights
Present main insights as paragraphs with subheadings. Minimize bullet points.

## Detailed Analysis
Deep-dive into patterns, comparisons, and implications.

## Challenges & Limitations
Explain challenges and known limitations.

## Recommendations
Provide actionable recommendations.

## Conclusion
Strong concluding paragraph summarizing findings.

## Sources
List all sources with title and URL.

RULES:
- Paragraphs over bullets
- No repetition
- Professional, academic tone
- Do NOT repeat information already in conversation history
"""

    def _followup_final_prompt(self, query, content, history_summary):
        return f"""
You are an advanced research writer handling a FOLLOW-UP question.

WHAT WAS ALREADY DISCUSSED:
{history_summary}

NEW FOLLOW-UP QUERY:
{query}

RESEARCH FOR THIS NEW ASPECT:
{content}

CRITICAL: This is a follow-up. The user already knows the basics from the prior conversation.
- DO NOT repeat the introduction or basics
- Focus EXCLUSIVELY on the new aspect the user is asking about
- Directly address what is NEW or DIFFERENT from prior discussion
- Be specific and concrete

FORMAT:
# [Title Reflecting the Specific Follow-Up]

## What's New / Specific to This Question
Directly answer the follow-up query. State clearly what differentiates this from the prior discussion.

## Focused Analysis
Deep-dive into the specific aspect asked about.

## Key Takeaways
Summarize in a short paragraph what the user should take away from this new information.

## Sources
List sources with title and URL.

RULES:
- No rehashing of prior conversation
- No generic introductions
- Stay tightly focused on the NEW question
"""

    def _partial_prompt(self, question, content, history_summary):
        return f"""
You are a professional research analyst.

CONTEXT:
{history_summary}

QUESTION:
{question}

RESEARCH FINDINGS:
{content}

Write a clear, focused paragraph-based answer to the question.
- Stay strictly on-topic
- Use the research content provided
- No bullet-heavy output
- Include sources (title + URL) at the end
"""
