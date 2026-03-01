import os
from dotenv import load_dotenv
from tavily import TavilyClient

# Load environment variables
load_dotenv()

# Get API key from .env
api_key = os.getenv("TAVILY_API_KEY")

# Initialize Tavily client
client = TavilyClient(api_key=api_key)

# Perform search
response = client.search(
    query="Latest AI news",
    search_depth="basic",
    max_results=3
)

print(response)