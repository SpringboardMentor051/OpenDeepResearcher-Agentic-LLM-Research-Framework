from dotenv import load_dotenv
import os 
load_dotenv()
from tavily import TavilyClient
import os

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

response = client.search("AI in healthcare")

print(response)
