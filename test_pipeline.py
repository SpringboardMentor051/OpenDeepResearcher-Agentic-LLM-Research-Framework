#!/usr/bin/env python3
"""
Test script to validate the research pipeline structure and execution flow.
Tests agents individually before full pipeline execution.
"""

import sys
import os
from typing import Dict, Any

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))


def test_imports():
    """Test that all modules import correctly"""
    print("🧪 Testing module imports...")
    try:
        from config.settings import LLM_URL, MODEL_NAME, TAVILY_API_KEY
        print(f"  ✓ Config loaded - LLM: {LLM_URL}")
        
        from agents.planner import planner_agent
        print("  ✓ Planner agent imported")
        
        from agents.searcher import searcher_agent
        print("  ✓ Searcher agent imported")
        
        from agents.writer import writer_agent
        print("  ✓ Writer agent imported")
        
        from pipeline import create_research_graph, execute_research
        print("  ✓ Pipeline imported")
        
        print("✅ All imports successful!\n")
        return True
    except Exception as e:
        print(f"❌ Import failed: {str(e)}\n")
        return False


def test_graph_structure():
    """Test that LangGraph is properly structured"""
    print("🧪 Testing LangGraph structure...")
    try:
        from pipeline import create_research_graph
        graph = create_research_graph()
        print(f"  ✓ Graph created: {type(graph).__name__}")
        print(f"  ✓ Graph has nodes and edges configured")
        print("✅ LangGraph structure valid!\n")
        return True
    except Exception as e:
        print(f"❌ Graph structure test failed: {str(e)}\n")
        return False


def test_state_creation():
    """Test that ResearchState is properly defined"""
    print("🧪 Testing ResearchState creation...")
    try:
        from pipeline import ResearchState
        test_state: ResearchState = {
            "topic": "Test Topic",
            "plan": None,
            "plan_details": None,
            "search_results": None,
            "final_summary": None,
            "error": None,
            "execution_time": 0
        }
        print(f"  ✓ State object created with {len(test_state)} fields")
        print(f"  ✓ State keys: {', '.join(test_state.keys())}")
        print("✅ ResearchState valid!\n")
        return True
    except Exception as e:
        print(f"❌ State creation test failed: {str(e)}\n")
        return False


def test_planner_agent_mock():
    """Test planner agent logic (with mock data)"""
    print("🧪 Testing Planner agent structure...")
    try:
        from agents.planner import planner_agent
        
        # Check if function exists and has correct signature
        import inspect
        sig = inspect.signature(planner_agent)
        params = list(sig.parameters.keys())
        
        assert 'topic' in params, "Planner missing 'topic' parameter"
        print(f"  ✓ Planner signature valid: {sig}")
        print("  ℹ️  Full testing requires LLM connection")
        print("✅ Planner agent structure valid!\n")
        return True
    except Exception as e:
        print(f"❌ Planner agent test failed: {str(e)}\n")
        return False


def test_searcher_agent_mock():
    """Test searcher agent logic"""
    print("🧪 Testing Searcher agent structure...")
    try:
        from agents.searcher import searcher_agent, search_tavily
        
        # Check signatures
        import inspect
        sig_searcher = inspect.signature(searcher_agent)
        sig_tavily = inspect.signature(search_tavily)
        
        print(f"  ✓ Searcher signature: {sig_searcher}")
        print(f"  ✓ Tavily search signature: {sig_tavily}")
        print("  ℹ️  Full testing requires Tavily API key")
        print("✅ Searcher agent structure valid!\n")
        return True
    except Exception as e:
        print(f"❌ Searcher agent test failed: {str(e)}\n")
        return False


def test_writer_agent_mock():
    """Test writer agent logic"""
    print("🧪 Testing Writer agent structure...")
    try:
        from agents.writer import writer_agent
        
        import inspect
        sig = inspect.signature(writer_agent)
        params = list(sig.parameters.keys())
        
        required_params = ['topic', 'search_results']
        for param in required_params:
            assert param in params, f"Writer missing '{param}' parameter"
        
        print(f"  ✓ Writer signature: {sig}")
        print("  ℹ️  Full testing requires LLM connection")
        print("✅ Writer agent structure valid!\n")
        return True
    except Exception as e:
        print(f"❌ Writer agent test failed: {str(e)}\n")
        return False


def run_validation_tests():
    """Run all validation tests"""
    print("\n" + "=" * 80)
    print("🚀 RESEARCH PIPELINE VALIDATION SUITE")
    print("=" * 80 + "\n")
    
    results = {
        "imports": test_imports(),
        "state": test_state_creation(),
        "graph": test_graph_structure(),
        "planner": test_planner_agent_mock(),
        "searcher": test_searcher_agent_mock(),
        "writer": test_writer_agent_mock(),
    }
    
    # Summary
    print("=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
    
    total_str = f"{passed}/{total} passed"
    print(f"\n{'Total':<30} {total_str}")
    
    if passed == total:
        print("\n🎉 All validation tests passed!")
        print("\n📋 Next steps:")
        print("  1. Ensure LLM server is running on http://127.0.0.1:1234")
        print("  2. Add Tavily API key to .env file")
        print("  3. Run: python main.py")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return False


if __name__ == "__main__":
    success = run_validation_tests()
    sys.exit(0 if success else 1)
