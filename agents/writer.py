from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
from os import getenv


class Writer:
    def __init__(self, model_name: str, base_url: str):
        self.client = OpenAI(
            base_url=base_url,
            api_key=getenv("API_KEY")
        )
        self.model = model_name

    def summarize(self, sub_question: str, search_content: str, history: list, is_followup: bool = False, final: bool = False) -> str:
        recent_history = history[-6:]

        history_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in recent_history
        ])

        # ---------------- FINAL OUTPUT ----------------
        if final and not is_followup:
             prompt = f"""
You are an advanced research writer.

Conversation Context:
{history_text}

Main Query:
{sub_question}

Collected Research:
{search_content}

Generate a structured research report in a PROFESSIONAL, PARAGRAPH-BASED format.

IMPORTANT WRITING STYLE:
- Write mostly in well-formed paragraphs with its headings of minimum 2 lines
- Avoid excessive bullet points
- Use smooth transitions between ideas
- Maintain academic tone

FORMAT:

# Title

## Introduction
Write a clear paragraph introducing the topic and its importance.

## Key Insights
Present insights primarily as paragraphs with its headings of minimum 2 lines(with their headings if present). Use bullet points ONLY if absolutely necessary.

## Detailed Analysis
Write detailed paragraphs explaining patterns, comparisons, and deeper insights(with its headings of minimum 2 lines if present).

## Challenges
Explain challenges in paragraph form with its headings of minimum 2 lines if present.

## Limitations
Discuss limitations in paragraph form with its headings of minimum 2 lines if present.

## Recommendations
Provide recommendations in paragraph form or bullets optional but minimal.

## Conclusion
Summarize the discussion in a strong concluding paragraph.

## Sources
List sources with title and URL.

RULES:
- Do NOT overuse bullet points
- Prefer paragraphs over lists
- Ensure smooth readability
- No repetition
"""


        elif final and is_followup:
            prompt = f"""
You are an advanced research writer.

This is a FOLLOW-UP question.

Conversation Context:
{history_text}

Query:
{sub_question}

Research:
{search_content}

INSTRUCTIONS:
- Do NOT repeat full introduction
- Focus only on the new aspect
- Build on previous discussion

WRITING STYLE:
- Use paragraph-based with their headings explanation
- Avoid bullet-heavy responses
- Keep it concise but fluid

FORMAT:

# Title

## Key Points
Explain in paragraph form with its subheadings(bullets only if necessary).

## Focused Analysis
Write a clear paragraph analyzing the topic.

## Conclusion
Summarize in a short paragraph.

## Sources
Must include include titles and URLs .

RULES:
- Paragraphs > bullets
- No redundancy
"""


        # ---------------- PARTIAL ----------------
        else:
            prompt = f"""
You are a professional research analyst.

Conversation Context:
{history_text}

Query:
{sub_question}

Research Findings:
{search_content}

Task:
- Generate a clear and structured answer

WRITING STYLE:
- Use paragraph-based explanation with its subheadings
- Avoid bullet-heavy output
- Ensure smooth flow

RULES:
- Only answer the query
- No repetition
- Include sources (title + URL)
"""


        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You write structured research summaries."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content