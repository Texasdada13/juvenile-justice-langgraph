"""
LangGraph Workflow Definition for Intake Triage Assistant

Defines the multi-agent workflow using LangGraph StateGraph.
"""

from typing import Literal
from langgraph.graph import StateGraph, END

from .state import IntakeState, IntakePhase
from .nodes import (
    intake_node,
    questioning_node,
    policy_retrieval_node,
    eligibility_node,
    risk_assessment_node,
    summary_node,
    human_review_node
)


def route_after_questioning(state: IntakeState) -> Literal["policy_retrieval", "questioning"]:
    """
    Route after questioning node based on topic coverage.

    Returns to questioning if topics remain uncovered,
    otherwise proceeds to policy retrieval.
    """
    uncovered = state.get("uncovered_topics", [])

    if uncovered and len(uncovered) > 0:
        return "questioning"
    else:
        return "policy_retrieval"


def route_after_review(state: IntakeState) -> Literal["questioning", "summary", "end"]:
    """
    Route after human review based on officer decision.

    - If additional questioning requested: Loop back
    - If edits made: Regenerate summary
    - Otherwise: End workflow (default for demo)
    """
    if state.get("request_additional_questioning"):
        return "questioning"
    elif state.get("officer_edits"):
        return "summary"
    else:
        # Default: end the workflow (for demo purposes, auto-approve)
        return "end"


def create_intake_graph() -> StateGraph:
    """
    Create the LangGraph workflow for intake triage.

    Returns:
        Compiled StateGraph
    """
    # Create the graph with our state schema
    workflow = StateGraph(IntakeState)

    # Add nodes
    workflow.add_node("intake", intake_node)
    workflow.add_node("questioning", questioning_node)
    workflow.add_node("policy_retrieval", policy_retrieval_node)
    workflow.add_node("eligibility", eligibility_node)
    workflow.add_node("risk_assessment", risk_assessment_node)
    workflow.add_node("summary", summary_node)
    workflow.add_node("human_review", human_review_node)

    # Set entry point
    workflow.set_entry_point("intake")

    # Add edges
    workflow.add_edge("intake", "questioning")

    # Conditional edge after questioning
    workflow.add_conditional_edges(
        "questioning",
        route_after_questioning,
        {
            "questioning": "questioning",
            "policy_retrieval": "policy_retrieval"
        }
    )

    # Linear flow through analysis nodes
    workflow.add_edge("policy_retrieval", "eligibility")
    workflow.add_edge("eligibility", "risk_assessment")
    workflow.add_edge("risk_assessment", "summary")
    workflow.add_edge("summary", "human_review")

    # Conditional edge after human review
    workflow.add_conditional_edges(
        "human_review",
        route_after_review,
        {
            "questioning": "questioning",
            "summary": "summary",
            "end": END
        }
    )

    return workflow


def compile_graph(checkpointer=None):
    """
    Compile the graph with optional checkpointing.

    Args:
        checkpointer: Optional checkpointer for state persistence

    Returns:
        Compiled graph ready for execution
    """
    workflow = create_intake_graph()

    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    else:
        return workflow.compile()


# Visualization helper
def get_graph_diagram() -> str:
    """
    Generate a text representation of the graph.

    Returns:
        ASCII diagram of the workflow
    """
    return """
    +-----------------------------------------------------------+
    |                 INTAKE TRIAGE WORKFLOW                    |
    +-----------------------------------------------------------+

    START
      |
      v
    +---------------+
    |    INTAKE     |  Collect basic information
    +---------------+
      |
      v
    +---------------+
    |  QUESTIONING  |<-----+  Generate & track questions
    +---------------+      |
      |                    |
      | (topics remain)    |
      +--------------------+
      | (all covered)
      v
    +------------------+
    | POLICY RETRIEVAL |  Query knowledge base
    +------------------+
      |
      v
    +---------------+
    |  ELIGIBILITY  |  Check program criteria
    +---------------+
      |
      v
    +-----------------+
    | RISK ASSESSMENT |  Evaluate risk factors
    +-----------------+
      |
      v
    +---------------+
    |    SUMMARY    |  Generate case summary
    +---------------+
      |
      v
    +---------------+
    | HUMAN REVIEW  |<----- INTERRUPT()
    +---------------+
      |
      +--- Approved ------> END (Case Created)
      |
      +--- More Info ----> QUESTIONING
      |
      +--- Edit ---------> SUMMARY
    """
