"""
Vector Store Management

Handles ChromaDB vector store for policy document storage and retrieval.
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path


# Default persist directory
DEFAULT_PERSIST_DIR = "./data/chroma"


def create_vector_store(
    documents: List[Dict[str, Any]],
    collection_name: str = "policies",
    persist_directory: Optional[str] = None
) -> Any:
    """
    Create a vector store from documents.

    Args:
        documents: List of documents with content and metadata
        collection_name: Name for the collection
        persist_directory: Directory to persist the database

    Returns:
        Vector store instance
    """
    try:
        import chromadb
        from chromadb.config import Settings

        persist_dir = persist_directory or os.getenv("CHROMA_PERSIST_DIR", DEFAULT_PERSIST_DIR)

        # Ensure directory exists
        Path(persist_dir).mkdir(parents=True, exist_ok=True)

        # Create client
        client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Juvenile justice policy documents"}
        )

        # Add documents
        ids = []
        contents = []
        metadatas = []

        for i, doc in enumerate(documents):
            doc_id = f"doc_{i}_{hash(doc['content'][:100]) % 10000}"
            ids.append(doc_id)
            contents.append(doc["content"])
            metadatas.append(doc.get("metadata", {}))

        if contents:
            collection.add(
                ids=ids,
                documents=contents,
                metadatas=metadatas
            )

        return collection

    except ImportError:
        print("ChromaDB not installed. Using in-memory mock store.")
        return MockVectorStore(documents)


def get_vector_store(
    collection_name: str = "policies",
    persist_directory: Optional[str] = None
) -> Any:
    """
    Get an existing vector store.

    Args:
        collection_name: Name of the collection
        persist_directory: Directory where database is stored

    Returns:
        Vector store instance
    """
    try:
        import chromadb
        from chromadb.config import Settings

        persist_dir = persist_directory or os.getenv("CHROMA_PERSIST_DIR", DEFAULT_PERSIST_DIR)

        client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )

        return client.get_collection(name=collection_name)

    except ImportError:
        print("ChromaDB not installed.")
        return None
    except Exception as e:
        print(f"Error getting vector store: {e}")
        return None


def add_documents(
    vector_store: Any,
    documents: List[Dict[str, Any]]
) -> None:
    """
    Add documents to an existing vector store.

    Args:
        vector_store: Vector store instance
        documents: Documents to add
    """
    if hasattr(vector_store, 'add'):
        ids = []
        contents = []
        metadatas = []

        existing_count = vector_store.count() if hasattr(vector_store, 'count') else 0

        for i, doc in enumerate(documents):
            doc_id = f"doc_{existing_count + i}_{hash(doc['content'][:100]) % 10000}"
            ids.append(doc_id)
            contents.append(doc["content"])
            metadatas.append(doc.get("metadata", {}))

        vector_store.add(
            ids=ids,
            documents=contents,
            metadatas=metadatas
        )


def query_vector_store(
    vector_store: Any,
    query: str,
    n_results: int = 5,
    where: Optional[Dict] = None
) -> List[Dict[str, Any]]:
    """
    Query the vector store for similar documents.

    Args:
        vector_store: Vector store instance
        query: Query string
        n_results: Number of results to return
        where: Optional metadata filter

    Returns:
        List of matching documents with scores
    """
    if hasattr(vector_store, 'query'):
        results = vector_store.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )

        # Format results
        documents = []
        if results and results.get('documents'):
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results.get('metadatas') else {},
                    "distance": results['distances'][0][i] if results.get('distances') else 0
                })

        return documents

    elif isinstance(vector_store, MockVectorStore):
        return vector_store.query(query, n_results)

    return []


class MockVectorStore:
    """
    Mock vector store for testing without ChromaDB.

    Uses simple keyword matching instead of embeddings.
    """

    def __init__(self, documents: List[Dict[str, Any]] = None):
        self.documents = documents or []

    def add(self, ids: List[str], documents: List[str], metadatas: List[Dict]):
        for i, doc in enumerate(documents):
            self.documents.append({
                "id": ids[i],
                "content": doc,
                "metadata": metadatas[i] if i < len(metadatas) else {}
            })

    def query(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Simple keyword-based search."""
        query_words = set(query.lower().split())

        scored = []
        for doc in self.documents:
            content_words = set(doc["content"].lower().split())
            overlap = len(query_words & content_words)
            if overlap > 0:
                scored.append((overlap, doc))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        return [
            {
                "content": doc["content"],
                "metadata": doc.get("metadata", {}),
                "distance": 1.0 / (score + 1)
            }
            for score, doc in scored[:n_results]
        ]

    def count(self) -> int:
        return len(self.documents)
