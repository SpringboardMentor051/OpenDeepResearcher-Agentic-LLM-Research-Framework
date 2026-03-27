import sys
import os

sys.path.append(os.path.abspath("../../"))

from milestone2.graph.pipeline import full_pipeline


def run_pipeline(query, chat_history=None):

    # add memory context (last 3 messages)
    if chat_history:
        context = "\n".join(
            [f"{m['role']}: {m['content']}" for m in chat_history[-3:]]
        )
        query = f"""
Previous conversation:
{context}

User question:
{query}
"""

    result = full_pipeline(query)

    return result   # clean text (no JSON)