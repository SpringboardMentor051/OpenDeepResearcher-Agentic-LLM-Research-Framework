from langchain_community.llms import Ollama

print("Starting LLM test...")

llm = Ollama(model="gemma:2b")

print("Sending request...")

response = llm.invoke("Explain machine learning in simple words.")

print("Response received:")
print(response)