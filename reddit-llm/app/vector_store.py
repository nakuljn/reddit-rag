from chromadb import Client
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import os

CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./data/chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "reddit_docs")


def get_chroma_client(persist_directory=CHROMA_DB_DIR):
    """Initialize and return a ChromaDB client."""
    return Client(Settings(persist_directory=persist_directory))


def get_or_create_collection(client=None, name=COLLECTION_NAME):
    """Get or create a ChromaDB collection for Reddit documents."""
    if client is None:
        client = get_chroma_client()
    if name in [c.name for c in client.list_collections()]:
        return client.get_collection(name)
    return client.create_collection(name)


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