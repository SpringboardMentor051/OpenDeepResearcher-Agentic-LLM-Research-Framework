from opensearch.planner import LLMPlanner

# Create planner instance
planner = LLMPlanner()

# Ask any question
response = planner.ask("What is machine learning?")
print(response)