"""Print versions of installed libraries."""

from importlib.metadata import version

print("Installed Library Versions:")
print("=" * 40)
print(f"langchain: {version('langchain')}")
print(f"langgraph: {version('langgraph')}")
print(f"tavily-python: {version('tavily-python')}")
print(f"python-dotenv: {version('python-dotenv')}") 