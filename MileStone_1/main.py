import warnings
warnings.filterwarnings("ignore")
from agent.planner import plan_query
from agent.searcher import search
from agent.writer import write_response
from dotenv import load_dotenv

load_dotenv()

def research_flow(topic: str):
    print(f"\nResearching Topic: {topic}\n")
    
    plan = plan_query(topic)
    
    context = search(topic)
    
    response = write_response(topic)
    
    print("\nPipeline complete!")
    return response

if __name__ == "__main__":
    topic = input("Enter your research topic: ")
    research_flow(topic)
