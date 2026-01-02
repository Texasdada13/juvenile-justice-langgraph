"""
Human Review & Approval Node

Handles human-in-the-loop review of the case summary before final
case creation. Uses LangGraph interrupt() for HITL workflow.
"""

from typing import Dict, Any
from ..state import IntakeState, IntakePhase


def human_review_node(state: IntakeState) -> IntakeState:
    """
    Human Review & Approval Node.

    This node:
    1. Displays case summary to officer
    2. Allows editing and notes
    3. Handles approval or request for additional info
    4. Logs decisions for audit trail

    In production, this would use interrupt() to pause for human input.
    For now, this is a placeholder that simulates the review process.

    Args:
        state: Current intake state

    Returns:
        Updated state after human review
    """
    # Update phase
    state["current_phase"] = IntakePhase.REVIEW.value

    # In production with LangGraph:
    # from langgraph.prebuilt import interrupt
    # interrupt("Please review the case summary and approve or edit.")

    state["messages"].append({
        "role": "system",
        "content": "Case summary ready for review. Awaiting officer approval."
    })

    return state


def process_approval(state: IntakeState, approved: bool, notes: str = "") -> IntakeState:
    """
    Process the officer's approval decision.

    Args:
        state: Current intake state
        approved: Whether the summary was approved
        notes: Officer's notes or edit requests

    Returns:
        Updated state with approval decision
    """
    state["approved"] = approved
    state["officer_notes"] = notes

    if approved:
        state["current_phase"] = IntakePhase.COMPLETE.value
        state["messages"].append({
            "role": "system",
            "content": f"Case {state['case_id']} approved and created in system."
        })
    else:
        # Request additional questioning or edits
        state["request_additional_questioning"] = True
        state["messages"].append({
            "role": "system",
            "content": f"Additional information requested: {notes}"
        })

    return state


def apply_edits(state: IntakeState, edits: Dict[str, str]) -> IntakeState:
    """
    Apply officer edits to the case summary.

    Args:
        state: Current intake state
        edits: Dictionary of field -> new value

    Returns:
        Updated state with applied edits
    """
    state["officer_edits"] = edits

    # Regenerate summary with edits applied
    # In production, this would re-run the summary generator
    # with the edited values incorporated

    state["messages"].append({
        "role": "system",
        "content": f"Applied {len(edits)} edits to case summary."
    })

    return state


def get_review_prompt(state: IntakeState) -> str:
    """
    Generate a prompt for the human reviewer.

    Args:
        state: Current intake state

    Returns:
        Review prompt string
    """
    risk_level = state.get("risk_level", "unknown")
    eligible_count = sum(
        1 for r in state.get("eligibility_results", [])
        if r.get("status") == "eligible"
    )

    return f"""
=== CASE REVIEW REQUIRED ===

Case ID: {state.get('case_id', 'N/A')}
Youth: {state.get('youth_info', {}).get('name', 'N/A')}
Risk Level: {risk_level.upper()}
Eligible Programs: {eligible_count}

Please review the case summary below and:
1. Verify accuracy of all information
2. Confirm eligibility determinations
3. Review risk assessment
4. Approve recommendations

Options:
[A] Approve - Create case in system
[E] Edit - Modify summary before approval
[M] More Info - Request additional questioning
[R] Reject - Start over

Enter your choice:
"""


def create_audit_record(state: IntakeState) -> Dict[str, Any]:
    """
    Create an audit record of the intake process.

    Args:
        state: Final intake state

    Returns:
        Audit record dictionary
    """
    return {
        "case_id": state.get("case_id"),
        "intake_officer": state.get("intake_officer"),
        "timestamp": state.get("timestamp"),
        "youth_name": state.get("youth_info", {}).get("name"),
        "referral_reason": state.get("referral_info", {}).get("reason"),
        "risk_level": state.get("risk_level"),
        "eligibility_results": [
            {
                "program": r.get("program_name"),
                "status": r.get("status"),
                "citation": r.get("policy_citation")
            }
            for r in state.get("eligibility_results", [])
        ],
        "recommendations": state.get("recommendations", []),
        "approved": state.get("approved"),
        "officer_notes": state.get("officer_notes"),
        "officer_edits": state.get("officer_edits"),
        "topics_covered": state.get("covered_topics", []),
        "questions_asked": len(state.get("responses", []))
    }
