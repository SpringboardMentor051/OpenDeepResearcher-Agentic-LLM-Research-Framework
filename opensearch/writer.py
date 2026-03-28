from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

def write_report(topic, research_data, history):

    print("\n Writer Agent generating research report with memory...\n")

    #  Convert history into proper message format (LIMITED history already passed)
    messages = [
        {"role": "system", "content": "You are an expert research report writer."}
    ]

    # Add previous conversation (already limited from app.py)
    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Add current prompt
    prompt = f"""
You are an expert AI research writer.

Use the conversation history to understand context.

Current Topic:
{topic}

IMPORTANT RULES:
- Use Markdown headings like ## Abstract
- Use ## only for main sections
- Use ### for subtopics inside sections
- Do NOT use numbering
- Do NOT use #### style headings
- Leave a blank line after each heading
- Use proper paragraphs

FORMAT:

## Abstract

## Introduction

## Methodology

## Literature Review

## Applications

## Challenges

## Future Improvements

## Conclusion

## Short Explanation

Research Information:
{research_data}
"""

    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="qwen2.5-vl-7b-instruct",
        messages=messages,   
        temperature=0.6,
        max_tokens=1500
    )

    return response.choices[0].message.content
