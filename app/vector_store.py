from chromadb import Client
from chromadb.config import Settings
from chromadb.utils import embedding_functions

import os

CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "reddit_docs")


def get_chroma_client(persist_directory=CHROMA_DB_DIR):
    """Initialize and return a ChromaDB client."""
    abs_path = os.path.abspath(persist_directory)
    print(f"[ChromaDB] Using persist_directory: {abs_path}")
    os.makedirs(abs_path, exist_ok=True)
    settings = Settings(persist_directory=abs_path, is_persistent=True)
    return Client(settings)


def get_or_create_collection(client=None, name=COLLECTION_NAME):
    """Get or create a ChromaDB collection for Reddit documents, using default embeddings."""
    if client is None:
        client = get_chroma_client()
        
    # Use default embedding function (sentence-transformers) - no API key required
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    if name in [c.name for c in client.list_collections()]:
        return client.get_collection(name, embedding_function=embedding_fn)
    return client.create_collection(name, embedding_function=embedding_fn)


def add_documents_to_collection(docs, collection=None):
    """
    Store a batch of documents in ChromaDB. Each doc must have 'id', 'text', and 'metadata'.
    """
    if collection is None:
        client = get_chroma_client()
        collection = get_or_create_collection(client)
    ids = [doc["id"] for doc in docs]
    texts = [doc["text"] for doc in docs]
    metadatas = [doc["metadata"] for doc in docs]
    collection.add(ids=ids, documents=texts, metadatas=metadatas)
    return len(ids) 