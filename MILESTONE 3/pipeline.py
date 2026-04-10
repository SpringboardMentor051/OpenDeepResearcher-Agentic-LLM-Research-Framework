"""
LangGraph-based Research Pipeline
Orchestrates Planner, Searcher, and Writer agents with RAG capabilities
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from agents.planner import planner_agent
from agents.searcher import searcher_agent
from agents.writer import writer_agent
from rag import get_research_rag, load_rag_knowledge_base, save_rag_knowledge_base
import json
import time


class ResearchState(TypedDict):
    """State object that flows through the graph"""
    topic: str
    plan: Optional[str]
    plan_details: Optional[dict]
    search_results: Optional[dict]
    final_summary: Optional[dict]
    error: Optional[str]
    logs: list
    execution_time: float


def validate_input(state: ResearchState) -> ResearchState:
    """Validate and prepare input"""
    if not state.get("topic"):
        state["error"] = "No topic provided"
    return state


def run_planner(state: ResearchState) -> ResearchState:
    """Run the Planner Agent"""
    state.setdefault("logs", [])
    try:
        state["logs"].append("📌 [Planning] Breaking down topic...")
        print("\n📌 [Planning] Breaking down topic...")
        result = planner_agent(state["topic"])
        state["plan_details"] = result
        state["plan"] = result.get("plan", "")
        state["logs"].append(f"✓ Plan created with {len(result.get('steps', []))} steps")
        print(f"✓ Plan created with {len(result.get('steps', []))} steps")
    except Exception as e:
        state["error"] = f"Planner error: {str(e)}"
        state["logs"].append(f"✗ Planner failed: {str(e)}")
        print(f"✗ Planner failed: {str(e)}")
    return state


def run_searcher(state: ResearchState) -> ResearchState:
    """Run the Searcher Agent"""
    if state.get("error"):
        return state
    
    state.setdefault("logs", [])
    try:
        state["logs"].append("🔍 [Searching] Fetching relevant content...")
        print("\n🔍 [Searching] Fetching relevant content...")
        result = searcher_agent(state.get("plan", ""), state["topic"])
        state["search_results"] = result
        total = result.get("total_results", 0)
        state["logs"].append(f"✓ Retrieved {total} search queries with results")
        print(f"✓ Retrieved {total} search queries with results")
    except Exception as e:
        state["error"] = f"Searcher error: {str(e)}"
        state["logs"].append(f"✗ Searcher failed: {str(e)}")
        print(f"✗ Searcher failed: {str(e)}")
    return state


def run_writer(state: ResearchState) -> ResearchState:
    """Run the Writer Agent"""
    if state.get("error"):
        return state
    
    state.setdefault("logs", [])
    try:
        state["logs"].append("✍️  [Synthesizing] Writing comprehensive summary...")
        print("\n✍️  [Synthesizing] Writing comprehensive summary...")
        content = state.get("search_results", {}).get("content_summary", "")
        result = writer_agent(
            topic=state["topic"],
            search_results=content,
            plan=state.get("plan", "")
        )
        state["final_summary"] = result
        state["logs"].append(f"✓ Summary written ({result.get('word_count', 0)} words)")
        print(f"✓ Summary written ({result.get('word_count', 0)} words)")
    except Exception as e:
        state["error"] = f"Writer error: {str(e)}"
        state["logs"].append(f"✗ Writer failed: {str(e)}")
        print(f"✗ Writer failed: {str(e)}")
    return state


def create_research_graph():
    """Create and compile the LangGraph research pipeline"""
    
    # Create the graph
    workflow = StateGraph(ResearchState)
    
    # Add nodes
    workflow.add_node("validate", validate_input)
    workflow.add_node("planner", run_planner)
    workflow.add_node("searcher", run_searcher)
    workflow.add_node("writer", run_writer)
    
    # Add edges (execution flow)
    workflow.set_entry_point("validate")
    workflow.add_edge("validate", "planner")
    workflow.add_edge("planner", "searcher")
    workflow.add_edge("searcher", "writer")
    workflow.add_edge("writer", END)
    
    # Compile the graph
    return workflow.compile()


def execute_research(topic: str) -> dict:
    """
    Execute the full research pipeline with RAG capabilities
    
    Args:
        topic: The research topic to investigate
        
    Returns:
        dict with execution results and metadata
    """
    start_time = time.time()
    
    # Load existing RAG knowledge base
    load_rag_knowledge_base()
    
    # Initialize state
    initial_state: ResearchState = {
        "topic": topic,
        "plan": None,
        "plan_details": None,
        "search_results": None,
        "final_summary": None,
        "error": None,
        "logs": [],
        "execution_time": 0
    }
    
    # Create and run graph
    graph = create_research_graph()
    
    print("=" * 60)
    print(f"🚀 Starting Research Pipeline for: {topic}")
    print("=" * 60)
    
    final_state = graph.invoke(initial_state)
    
    execution_time = time.time() - start_time
    final_state["execution_time"] = execution_time
    
    # Save updated RAG knowledge base
    save_rag_knowledge_base()
    
    print("\n" + "=" * 60)
    print("📊 Research Pipeline Completed")
    print("=" * 60)
    
    return {
        "topic": topic,
        "status": "success" if not final_state.get("error") else "failed",
        "error": final_state.get("error"),
        "plan": final_state.get("plan_details"),
        "search_results": final_state.get("search_results"),
        "summary": final_state.get("final_summary"),
        "execution_time": execution_time,
        "logs": final_state.get("logs", []),
    }


if __name__ == "__main__":
    # Test the pipeline
    test_topic = "Artificial Intelligence in Healthcare"
    result = execute_research(test_topic)
    
    print("\n📋 Final Summary:")
    print(result["summary"]["summary"] if result.get("summary") else "No summary generated")
