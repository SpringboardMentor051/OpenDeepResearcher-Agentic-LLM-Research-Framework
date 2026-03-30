def planner_agent(query):
    sub_questions = [
        f"What is {query}?",
        f"Advantages of {query}?",
        f"Challenges of {query}?"
    ]
    return sub_questions