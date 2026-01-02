"""
Policy Retrieval Agent Node

Retrieves relevant policies, eligibility rules, and prior case patterns
from the knowledge base using RAG.
"""

from typing import Dict, Any, List
from ..state import IntakeState, IntakePhase, PolicyDocument


def extract_query_context(state: IntakeState) -> Dict[str, Any]:
    """
    Extract key facts from state to form retrieval queries.

    Args:
        state: Current intake state

    Returns:
        Dictionary of key facts for querying
    """
    youth_info = state.get("youth_info", {})
    referral_info = state.get("referral_info", {})
    responses = state.get("responses", [])

    # Extract key facts
    context = {
        "age": youth_info.get("age"),
        "offense": referral_info.get("reason"),
        "risk_factors": [],
        "needs": []
    }

    # Extract risk factors and needs from responses
    for qa in responses:
        topic = qa.get("topic", "")
        answer = qa.get("answer", "").lower()

        # Identify substance use
        if topic == "substance_use" and any(word in answer for word in ["yes", "marijuana", "alcohol", "drugs"]):
            context["risk_factors"].append("substance_use")
            context["needs"].append("substance_abuse_treatment")

        # Identify mental health needs
        if topic == "mental_health" and any(word in answer for word in ["yes", "diagnosed", "treatment", "therapy"]):
            context["needs"].append("mental_health_services")

        # Identify education issues
        if topic == "education" and any(word in answer for word in ["truant", "suspended", "expelled", "failing"]):
            context["risk_factors"].append("education_issues")
            context["needs"].append("educational_support")

        # Identify family issues
        if topic == "family_situation" and any(word in answer for word in ["conflict", "divorce", "absent", "unstable"]):
            context["risk_factors"].append("family_instability")
            context["needs"].append("family_counseling")

    return context


def build_retrieval_queries(context: Dict[str, Any]) -> List[str]:
    """
    Build retrieval queries based on extracted context.

    Args:
        context: Dictionary of key facts

    Returns:
        List of retrieval queries
    """
    queries = []

    # Base eligibility query
    if context.get("age") and context.get("offense"):
        queries.append(
            f"Eligibility requirements for {context['age']} year old charged with {context['offense']}"
        )

    # Risk-based queries
    if context.get("risk_factors"):
        for factor in context["risk_factors"]:
            queries.append(f"Risk assessment criteria for youth with {factor.replace('_', ' ')}")

    # Needs-based queries
    if context.get("needs"):
        for need in context["needs"]:
            queries.append(f"Program eligibility for {need.replace('_', ' ')}")

    # Default query if no specific context
    if not queries:
        queries.append("Juvenile diversion program eligibility criteria")

    return queries


def policy_retrieval_node(state: IntakeState) -> IntakeState:
    """
    Policy Retrieval Agent Node.

    This node:
    1. Extracts key facts from collected information
    2. Queries vector store for relevant policies
    3. Finds similar prior cases
    4. Stores retrieved documents in state

    Note: This is a placeholder implementation. In production,
    this would connect to the actual vector store.

    Args:
        state: Current intake state

    Returns:
        Updated state with retrieved policies
    """
    # Update phase
    state["current_phase"] = IntakePhase.POLICY_RETRIEVAL.value

    # Extract context for queries
    context = extract_query_context(state)

    # Build queries
    queries = build_retrieval_queries(context)

    # Log queries
    state["messages"].append({
        "role": "system",
        "content": f"Retrieving policies for: {', '.join(queries[:3])}"
    })

    # Placeholder: In production, this would query the vector store
    # For now, create mock retrieved documents
    mock_policies = create_mock_policies(context)

    # Store in state
    state["retrieved_policies"] = mock_policies

    # Update phase to eligibility
    state["current_phase"] = IntakePhase.ELIGIBILITY.value

    state["messages"].append({
        "role": "system",
        "content": f"Retrieved {len(mock_policies)} relevant policy documents. Moving to eligibility checking."
    })

    return state


def create_mock_policies(context: Dict[str, Any]) -> List[PolicyDocument]:
    """
    Create mock policy documents for testing.

    In production, this would be replaced by actual RAG retrieval.

    Args:
        context: Query context

    Returns:
        List of mock policy documents
    """
    policies: List[PolicyDocument] = []

    # Mock diversion eligibility policy
    policies.append({
        "content": """
        Youth Diversion Program Eligibility Criteria:
        1. Age: 12-17 years old
        2. Offense: Non-violent misdemeanor or low-level felony
        3. Prior record: First-time or second-time offender
        4. Risk level: Low to moderate risk
        5. Family involvement: Guardian willing to participate
        6. Exclusions: Sexual offenses, firearms offenses, gang-related violence
        """,
        "source": "County Diversion Policy Manual",
        "section": "Section 3.2 - Eligibility Criteria",
        "relevance_score": 0.92,
        "metadata": {
            "policy_type": "eligibility",
            "effective_date": "2024-01-01",
            "jurisdiction": "county"
        }
    })

    # Add needs-specific policies
    if "substance_abuse_treatment" in context.get("needs", []):
        policies.append({
            "content": """
            Substance Abuse Treatment Program Requirements:
            1. Documented substance use issue
            2. Youth and family consent to treatment
            3. Assessment by licensed substance abuse counselor
            4. Medicaid or private insurance (or county funding available)
            5. Commitment to 12-week minimum program
            """,
            "source": "Treatment Services Guide",
            "section": "Section 5.1 - Substance Abuse Services",
            "relevance_score": 0.88,
            "metadata": {
                "policy_type": "treatment_eligibility",
                "effective_date": "2024-01-01",
                "jurisdiction": "county"
            }
        })

    if "mental_health_services" in context.get("needs", []):
        policies.append({
            "content": """
            Mental Health Services Eligibility:
            1. Screening indicates mental health needs
            2. Youth agrees to participate in services
            3. Services can be provided in least restrictive setting
            4. Priority given to youth with documented diagnoses
            5. Trauma-informed care available for abuse/trauma history
            """,
            "source": "Mental Health Services Policy",
            "section": "Section 4.2 - Eligibility",
            "relevance_score": 0.85,
            "metadata": {
                "policy_type": "mental_health",
                "effective_date": "2024-01-01",
                "jurisdiction": "county"
            }
        })

    # Add risk assessment policy
    policies.append({
        "content": """
        Risk Assessment Protocol:
        All youth must be assessed using the validated risk assessment instrument.
        Risk levels determine appropriate intervention:
        - Low risk: Diversion, minimal supervision
        - Moderate risk: Probation with services
        - High risk: Intensive supervision, possible placement
        - Very high risk: Secure placement consideration

        Risk factors include: prior offenses, family instability, substance use,
        peer associations, education problems, mental health issues.

        Protective factors to consider: family support, school engagement,
        prosocial activities, positive peer relationships, future orientation.
        """,
        "source": "Risk Assessment Policy",
        "section": "Section 2.1 - Assessment Protocol",
        "relevance_score": 0.90,
        "metadata": {
            "policy_type": "risk_assessment",
            "effective_date": "2024-01-01",
            "jurisdiction": "county"
        }
    })

    return policies


async def retrieve_from_vector_store(
    queries: List[str],
    vector_store: Any,
    top_k: int = 5
) -> List[PolicyDocument]:
    """
    Retrieve documents from vector store.

    This is the production implementation that connects to the actual
    vector store (ChromaDB, Pinecone, etc.)

    Args:
        queries: List of retrieval queries
        vector_store: Vector store instance
        top_k: Number of documents to retrieve per query

    Returns:
        List of retrieved policy documents
    """
    # Placeholder - would implement actual retrieval here
    # Example with LangChain:
    #
    # from langchain.retrievers import MultiQueryRetriever
    # retriever = MultiQueryRetriever.from_llm(
    #     retriever=vector_store.as_retriever(search_kwargs={"k": top_k}),
    #     llm=llm
    # )
    # docs = retriever.get_relevant_documents(queries[0])

    pass
