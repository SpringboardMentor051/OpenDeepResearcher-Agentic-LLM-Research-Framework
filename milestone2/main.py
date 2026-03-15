from graph.pipeline import full_pipeline

query = input("Enter research topic: ")

report = full_pipeline(query)

print(report)