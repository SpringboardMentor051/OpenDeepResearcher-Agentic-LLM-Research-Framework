from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

def write_report(topic, research_data):

    print("\n Writer Agent generating research report...\n")

    prompt = f"""
You are an expert AI research writer.

Using the research information below, generate a well-structured research report.

Topic: {topic}

Use the following sections:
1. Abstract
2. Introduction
3. Methodology
4. Literature Review
5.Applications
6. Challenges
7. Future Improvements
8. Conclusion
9. References
10.Short Explanation

Research Information:
{research_data}

Write a detailed report.
"""

    response = client.chat.completions.create(
        model="qwen2.5-vl-7b-instruct",
        messages=[
            {"role": "system", "content": "You are an expert research report writer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
        max_tokens=1200
    )

    report = response.choices[0].message.content

    return report
