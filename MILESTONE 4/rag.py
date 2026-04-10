"""
RAG (Retrieval-Augmented Generation) System
Provides document storage, retrieval, and context augmentation for the research pipeline
"""

from typing import List, Dict, Any
import faiss
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
from config.settings import LLM_API_KEY
import os
import re


class LocalEmbeddings:
    """Local embeddings using sentence-transformers directly"""
    
    def __init__(self):
        self.model = None
        self._loaded = False
    
    def _load_model(self):
        if not self._loaded:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self._loaded = True
            except ImportError:
                raise ImportError("sentence_transformers not available. Install with: pip install sentence-transformers")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        self._load_model()
        return self.model.encode(texts, convert_to_numpy=True).tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        self._load_model()
        return self.model.encode([text], convert_to_numpy=True)[0].tolist()


class SimpleTextSplitter:
    """Simple text splitter that doesn't depend on sentence-transformers"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        split_docs = []
        for doc in documents:
            chunks = self._split_text(doc.page_content)
            for chunk in chunks:
                split_docs.append(Document(
                    page_content=chunk,
                    metadata=doc.metadata
                ))
        return split_docs
    
    def _split_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            
            # If we're not at the end, try to find a good break point
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                last_period = text.rfind('.', start, end)
                last_newline = text.rfind('\n', start, end)
                break_point = max(last_period, last_newline)
                
                if break_point > start + self.chunk_size - 100:
                    end = break_point + 1
                else:
                    # Look for word boundaries
                    last_space = text.rfind(' ', start, end)
                    if last_space > start:
                        end = last_space
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = max(start + 1, end - self.chunk_overlap)
        
        return chunks


class ResearchRAG:
    """RAG system for storing and retrieving research documents"""

    def __init__(self):
        # Initialize embeddings lazily
        self.embeddings = LocalEmbeddings()
        self._embeddings_loaded = True  # LocalEmbeddings loads lazily internally
        
        # Initialize text splitter
        self.text_splitter = SimpleTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Initialize vector store
        self.vectorstore = None
        self.docstore = InMemoryDocstore({})
        self.index_to_docstore_id = {}

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the RAG system

        Args:
            documents: List of document dicts with 'title', 'content', 'source' keys
        """
        if not documents:
            return

        # Convert to LangChain documents
        langchain_docs = []
        for doc in documents:
            content = doc.get('content', '')
            if content:
                metadata = {
                    'title': doc.get('title', 'Unknown'),
                    'source': doc.get('source', 'Unknown'),
                    'query': doc.get('query', '')
                }
                langchain_docs.append(Document(page_content=content, metadata=metadata))

        if not langchain_docs:
            return

        # Split documents into chunks
        split_docs = self.text_splitter.split_documents(langchain_docs)

        # Create or update vector store
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(split_docs, self.embeddings)
        else:
            self.vectorstore.add_documents(split_docs)

    def retrieve_relevant_context(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks for a query

        Args:
            query: Search query
            k: Number of relevant chunks to retrieve

        Returns:
            List of relevant document chunks with metadata
        """
        if self.vectorstore is None:
            return []

        try:
            # Search for similar documents
            docs = self.vectorstore.similarity_search(query, k=k)

            # Convert back to dict format
            results = []
            for doc in docs:
                results.append({
                    'content': doc.page_content,
                    'title': doc.metadata.get('title', 'Unknown'),
                    'source': doc.metadata.get('source', 'Unknown'),
                    'query': doc.metadata.get('query', ''),
                    'similarity_score': getattr(doc, 'score', None)  # If available
                })

            return results

        except Exception as e:
            print(f"RAG retrieval error: {e}")
            return []

    def get_context_for_topic(self, topic: str, plan: str = "", k: int = 10) -> str:
        """
        Get relevant context for a research topic

        Args:
            topic: Research topic
            plan: Research plan for additional context
            k: Number of chunks to retrieve

        Returns:
            Formatted context string
        """
        # Create comprehensive query
        query = f"{topic}"
        if plan:
            query += f" {plan[:200]}"  # Add part of the plan

        relevant_docs = self.retrieve_relevant_context(query, k=k)

        if not relevant_docs:
            return "No relevant context found in knowledge base."

        # Format context
        context_parts = []
        for i, doc in enumerate(relevant_docs, 1):
            context_parts.append(f"[Context {i}]")
            context_parts.append(f"Title: {doc['title']}")
            context_parts.append(f"Source: {doc['source']}")
            context_parts.append(f"Content: {doc['content']}")
            context_parts.append("")

        return "\n".join(context_parts)


# Global RAG instance - created lazily
_research_rag_instance = None

def get_research_rag() -> ResearchRAG:
    """Get the global RAG instance, creating it if needed"""
    global _research_rag_instance
    if _research_rag_instance is None:
        _research_rag_instance = ResearchRAG()
    return _research_rag_instance

# For backward compatibility
research_rag = None  # Will be set when first accessed


def save_rag_knowledge_base(filepath: str = "research_knowledge_base.faiss") -> None:
    """
    Save the RAG knowledge base to disk

    Args:
        filepath: Path to save the knowledge base
    """
    rag_instance = get_research_rag()
    if rag_instance.vectorstore:
        rag_instance.vectorstore.save_local(filepath)
        print(f"RAG knowledge base saved to {filepath}")


def load_rag_knowledge_base(filepath: str = "research_knowledge_base.faiss") -> None:
    """
    Load the RAG knowledge base from disk

    Args:
        filepath: Path to load the knowledge base from
    """
    try:
        if not os.path.exists(os.path.join(filepath, "index.faiss")):
            print(f"No existing RAG knowledge base found at {filepath}. Starting with empty knowledge base.")
            return

        rag_instance = get_research_rag()
        rag_instance.vectorstore = FAISS.load_local(filepath, rag_instance.embeddings, allow_dangerous_deserialization=True)
        print(f"RAG knowledge base loaded from {filepath}")
    except Exception as e:
        print(f"Could not load RAG knowledge base: {e}")
        print("Starting with empty knowledge base")