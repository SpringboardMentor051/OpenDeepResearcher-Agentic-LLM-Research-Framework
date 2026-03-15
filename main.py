#!/usr/bin/env python3
"""
Open Researcher Project - Main Entry Point
Orchestrates the research pipeline using LangGraph
"""

from pipeline import execute_research
import json
from datetime import datetime


def format_results(result: dict) -> str:
    """Format execution results for display"""
    output = []
    output.append("\n" + "=" * 80)
    output.append("RESEARCH RESULTS")
    output.append("=" * 80)
    
    output.append(f"\n📝 Topic: {result['topic']}")
    output.append(f"Status: {'✅ Success' if result['status'] == 'success' else '❌ Failed'}")
    output.append(f"⏱️  Execution Time: {result['execution_time']:.2f} seconds")
    
    if result.get("error"):
        output.append(f"\n⚠️  Error: {result['error']}")
        return "\n".join(output)
    
    # Planning phase
    if result.get("plan"):
        output.append("\n" + "-" * 80)
        output.append("🎯 RESEARCH PLAN")
        output.append("-" * 80)
        output.append(result["plan"].get("plan", ""))
    
    # Search phase
    if result.get("search_results"):
        output.append("\n" + "-" * 80)
        output.append("🔍 SEARCH RESULTS")
        output.append("-" * 80)
        output.append(f"Found {result['search_results'].get('total_results', 0)} queries with results")
    
    # Final summary
    if result.get("summary"):
        output.append("\n" + "-" * 80)
        output.append("📄 FINAL SUMMARY")
        output.append("-" * 80)
        output.append(result["summary"].get("summary", ""))
        
        if result["summary"].get("key_points"):
            output.append("\n🔑 Key Points:")
            for point in result["summary"]["key_points"]:
                if point.strip():
                    output.append(f"  • {point}")
    
    output.append("\n" + "=" * 80)
    return "\n".join(output)


def run_research(topic: str) -> dict:
    """
    Main research execution function
    
    Args:
        topic: The research topic to investigate
        
    Returns:
        Research results dictionary
    """
    return execute_research(topic)


def main():
    """Main entry point"""
    print("\n🤖 Open Researcher - Powered by LangGraph")
    print("-" * 80)
    
    # Ask for topic directly
    topic = input("Enter research topic: ")
    
    if not topic.strip():
        print("Error: Topic cannot be empty")
        return
        
    result = run_research(topic)
    formatted_output = format_results(result)
    print(formatted_output)
    
    # Save results to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"research_result_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Results saved to: {filename}")


if __name__ == "__main__":
    main()

