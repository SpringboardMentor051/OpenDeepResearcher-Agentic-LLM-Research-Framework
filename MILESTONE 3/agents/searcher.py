import requests
from config.settings import TAVILY_API_KEY, MAX_SEARCH_RESULTS
from typing import List, Dict
from rag import get_research_rag
import datetime

def search_tavily(query: str, max_results: int = None) -> List[Dict]:
    """
    Search using Tavily API for research content.
    
    Args:
        query: Search query string
        max_results: Maximum number of search results to return
        
    Returns:
        List of search results with title, content, and source
    """
    if max_results is None:
        max_results = MAX_SEARCH_RESULTS
        
    if not TAVILY_API_KEY:
        return [{"error": "Tavily API key not configured"}]
    
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": max_results,
        "include_answer": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except requests.exceptions.RequestException as e:
        return [{"error": f"Search failed: {str(e)}"}]


def searcher_agent(plan: str, topic: str = "") -> dict:
    """
    Searcher Agent: Fetches relevant content based on research plan.
    
    Args:
        plan: The research plan/steps to search for
        topic: Original research topic for context
        
    Returns:
        dict with 'search_results', 'queries', and 'content_summary' keys
    """
    # Extract search queries from plan
    search_queries = []
    for line in plan.split('\n'):
        line = line.strip()
        if line and not line.startswith(('Step', 'step', '#', '-')):
            if len(line) > 10:  # Only meaningful lines
                search_queries.append(line)
    
    if not search_queries:
        search_queries = [plan[:100], topic]  # Fallback
    
    results = []
    all_content = []
    
    for query in search_queries[:3]:  # Limit to 3 searches to balance speed and quality
        search_results = search_tavily(query, MAX_SEARCH_RESULTS)
        if search_results and "error" not in search_results[0]:
            results.append({
                "query": query,
                "results": search_results
            })
            
            # Aggregate content for summary
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for result in search_results:
                if isinstance(result, dict) and "content" in result:
                    title = result.get('title', 'N/A')
                    url = result.get('url', 'Unknown')
                    all_content.append(f"Source: {title}\nURL: {url}\nTimestamp: {timestamp}\nContent: {result['content']}")
                    
                    # Add to RAG system
                    rag_doc = {
                        'title': result.get('title', 'Unknown'),
                        'content': result.get('content', ''),
                        'source': result.get('url', 'Unknown'),
                        'query': query
                    }
                    get_research_rag().add_documents([rag_doc])
    
    content_summary = "\n\n".join(all_content[:8])  # Use top 8 results to give more context
    
    return {
        "search_results": results,
        "total_results": len(results),
        "content_summary": content_summary if content_summary else "No search results found. Using general knowledge."
    }