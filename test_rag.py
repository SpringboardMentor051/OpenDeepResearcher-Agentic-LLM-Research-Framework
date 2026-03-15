#!/usr/bin/env python3
"""
Test RAG functionality
"""

from rag import research_rag, save_rag_knowledge_base, load_rag_knowledge_base

def test_rag():
    """Test the RAG system"""
    print("Testing RAG System...")

    # Add some test documents
    test_docs = [
        {
            'title': 'AI in Healthcare Overview',
            'content': 'Artificial Intelligence is transforming healthcare by enabling better diagnostics, personalized treatment plans, and drug discovery. Machine learning algorithms can analyze medical images with high accuracy, predict patient outcomes, and identify patterns in large datasets.',
            'source': 'medical_journal.com',
            'query': 'AI healthcare applications'
        },
        {
            'title': 'Machine Learning for Disease Prediction',
            'content': 'Recent advances in machine learning have improved disease prediction accuracy by 30%. Deep learning models trained on electronic health records can predict patient readmission risks and suggest preventive measures.',
            'source': 'ai_research.org',
            'query': 'machine learning healthcare'
        }
    ]

    # Add documents to RAG
    research_rag.add_documents(test_docs)
    print("✓ Added test documents to RAG")

    # Test retrieval
    query = "AI applications in healthcare diagnostics"
    results = research_rag.retrieve_relevant_context(query, k=3)
    print(f"✓ Retrieved {len(results)} relevant chunks for query: '{query}'")

    # Test context generation
    context = research_rag.get_context_for_topic("Artificial Intelligence in Healthcare")
    print("✓ Generated context for topic")
    print(f"Context length: {len(context)} characters")

    # Save and load test
    save_rag_knowledge_base("test_knowledge_base.faiss")
    print("✓ Saved knowledge base")

    # Clear and reload
    research_rag.vectorstore = None
    load_rag_knowledge_base("test_knowledge_base.faiss")
    print("✓ Loaded knowledge base")

    # Test retrieval after reload
    results_after_load = research_rag.retrieve_relevant_context(query, k=2)
    print(f"✓ Retrieved {len(results_after_load)} chunks after reload")

    print("\n🎉 RAG System Test Completed Successfully!")

if __name__ == "__main__":
    test_rag()