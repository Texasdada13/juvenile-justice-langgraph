"""
Retriever Components

Implements retrieval strategies for the knowledge base.
"""

from typing import List, Dict, Any, Optional
from .vector_store import query_vector_store


def create_retriever(
    vector_store: Any,
    search_type: str = "similarity",
    top_k: int = 5
) -> "PolicyRetriever":
    """
    Create a retriever instance.

    Args:
        vector_store: Vector store to retrieve from
        search_type: Type of search (similarity, mmr, etc.)
        top_k: Default number of results

    Returns:
        PolicyRetriever instance
    """
    return PolicyRetriever(
        vector_store=vector_store,
        search_type=search_type,
        top_k=top_k
    )


def retrieve_policies(
    vector_store: Any,
    query: str,
    top_k: int = 5,
    metadata_filter: Optional[Dict] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant policies from vector store.

    Args:
        vector_store: Vector store instance
        query: Search query
        top_k: Number of results
        metadata_filter: Optional filter on metadata

    Returns:
        List of relevant documents
    """
    return query_vector_store(
        vector_store=vector_store,
        query=query,
        n_results=top_k,
        where=metadata_filter
    )


class PolicyRetriever:
    """
    Retriever for policy documents.

    Supports multiple retrieval strategies and query expansion.
    """

    def __init__(
        self,
        vector_store: Any,
        search_type: str = "similarity",
        top_k: int = 5
    ):
        self.vector_store = vector_store
        self.search_type = search_type
        self.top_k = top_k

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        metadata_filter: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents.

        Args:
            query: Search query
            top_k: Number of results (overrides default)
            metadata_filter: Optional metadata filter

        Returns:
            List of relevant documents
        """
        k = top_k or self.top_k

        return query_vector_store(
            vector_store=self.vector_store,
            query=query,
            n_results=k,
            where=metadata_filter
        )

    def retrieve_for_eligibility(
        self,
        age: int,
        offense: str,
        risk_level: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve eligibility-related policies.

        Args:
            age: Youth's age
            offense: Offense type
            risk_level: Risk level

        Returns:
            Relevant eligibility policies
        """
        queries = [
            f"Eligibility requirements for {age} year old",
            f"Program eligibility for {offense} offense",
            f"Diversion eligibility criteria for {risk_level} risk youth"
        ]

        all_results = []
        for query in queries:
            results = self.retrieve(
                query,
                metadata_filter={"policy_type": "eligibility"}
            )
            all_results.extend(results)

        # Deduplicate by content
        seen = set()
        unique = []
        for doc in all_results:
            content_hash = hash(doc["content"][:100])
            if content_hash not in seen:
                seen.add(content_hash)
                unique.append(doc)

        return unique[:self.top_k]

    def retrieve_for_risk_assessment(
        self,
        risk_factors: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Retrieve risk assessment policies.

        Args:
            risk_factors: List of identified risk factors

        Returns:
            Relevant risk assessment policies
        """
        query = f"Risk assessment criteria for youth with {', '.join(risk_factors)}"

        return self.retrieve(
            query,
            metadata_filter={"policy_type": "risk_assessment"}
        )

    def multi_query_retrieve(
        self,
        queries: List[str],
        top_k_per_query: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve using multiple queries and combine results.

        Args:
            queries: List of search queries
            top_k_per_query: Results per query

        Returns:
            Combined and deduplicated results
        """
        all_results = []

        for query in queries:
            results = self.retrieve(query, top_k=top_k_per_query)
            all_results.extend(results)

        # Deduplicate and re-rank by average score
        content_scores = {}
        for doc in all_results:
            key = hash(doc["content"][:100])
            if key not in content_scores:
                content_scores[key] = {
                    "doc": doc,
                    "scores": []
                }
            content_scores[key]["scores"].append(1.0 - doc.get("distance", 0.5))

        # Average scores
        ranked = []
        for key, data in content_scores.items():
            avg_score = sum(data["scores"]) / len(data["scores"])
            data["doc"]["avg_score"] = avg_score
            ranked.append(data["doc"])

        # Sort by average score
        ranked.sort(key=lambda x: x.get("avg_score", 0), reverse=True)

        return ranked[:self.top_k]


# LangChain integration
def create_langchain_retriever(vector_store: Any) -> Any:
    """
    Create a LangChain-compatible retriever.

    Args:
        vector_store: ChromaDB collection or LangChain vector store

    Returns:
        LangChain retriever
    """
    try:
        from langchain.vectorstores import Chroma
        from langchain.retrievers import MultiQueryRetriever

        # If it's already a LangChain vector store
        if hasattr(vector_store, 'as_retriever'):
            return vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )

        # Otherwise wrap it
        # This would require embeddings model
        return None

    except ImportError:
        return None
