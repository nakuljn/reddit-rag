from app.vector_store import get_chroma_client, get_or_create_collection
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
import os

COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "reddit_docs")


def search_similar_documents(query, top_k=5, collection=None, embedding_fn=None):
    """
    Search for documents most similar to the query in ChromaDB.
    Returns a list of dicts with document text and metadata.
    """
    if not query or not query.strip():
        return []
    
    if collection is None:
        client = get_chroma_client()
        collection = get_or_create_collection(client, name=COLLECTION_NAME)
    if embedding_fn is None:
        embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    
    try:
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Handle empty results
        if not results["ids"] or not results["ids"][0]:
            return []
        
        docs = []
        for i in range(len(results["ids"][0])):
            docs.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if "distances" in results else None
            })
        return docs
    except Exception as e:
        # Log error and return empty list instead of crashing
        print(f"Search failed: {str(e)}")
        return []


def search_with_multiple_queries(queries: List[str], top_k=5) -> List[Dict[str, Any]]:
    """
    Search using multiple query variations and combine results.
    Deduplicates and ranks by best distance scores.
    """
    if not queries:
        return []
    
    all_docs = {}  # Use dict to deduplicate by ID
    
    client = get_chroma_client()
    collection = get_or_create_collection(client, name=COLLECTION_NAME)
    
    # Search with each query variation
    for query in queries:
        if not query or not query.strip():
            continue
        
        docs = search_similar_documents(query, top_k=top_k, collection=collection)
        
        # Add to results, keeping best distance score for each document
        for doc in docs:
            doc_id = doc["id"]
            if doc_id not in all_docs or (doc["distance"] and doc["distance"] < all_docs[doc_id]["distance"]):
                all_docs[doc_id] = doc
    
    # Convert back to list and sort by distance (best first)
    combined_docs = list(all_docs.values())
    combined_docs.sort(key=lambda x: x["distance"] if x["distance"] is not None else float('inf'))
    
    # Return top_k results
    return combined_docs[:top_k]

