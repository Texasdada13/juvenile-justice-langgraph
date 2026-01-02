"""
Case Intake Node

Handles initial case intake: collects basic information, validates required fields,
and initializes case state.
"""

from typing import Dict, Any
from datetime import datetime
from ..state import IntakeState, IntakePhase


def validate_youth_info(youth_info: Dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate that required youth information is present.

    Args:
        youth_info: Dictionary containing youth information

    Returns:
        Tuple of (is_valid, list of missing fields)
    """
    required_fields = ["name", "date_of_birth"]
    missing = [field for field in required_fields if not youth_info.get(field)]
    return len(missing) == 0, missing


def calculate_age(date_of_birth: str) -> int:
    """
    Calculate age from date of birth.

    Args:
        date_of_birth: Date of birth string (YYYY-MM-DD format)

    Returns:
        Age in years
    """
    try:
        dob = datetime.fromisoformat(date_of_birth)
        today = datetime.now()
        age = today.year - dob.year
        if (today.month, today.day) < (dob.month, dob.day):
            age -= 1
        return age
    except (ValueError, TypeError):
        return -1


def intake_node(state: IntakeState) -> IntakeState:
    """
    Case Intake Node - Initialize case and validate basic information.

    This node:
    1. Validates required youth information
    2. Calculates youth's age
    3. Sets up initial case state
    4. Prepares for structured questioning

    Args:
        state: Current intake state

    Returns:
        Updated state with validated intake information
    """
    # Get youth info from state
    youth_info = state.get("youth_info", {})

    # Validate required fields
    is_valid, missing_fields = validate_youth_info(youth_info)

    if not is_valid:
        # If critical info missing, note the error but continue
        state["error"] = f"Missing required fields: {', '.join(missing_fields)}"
        state["messages"].append({
            "role": "system",
            "content": f"Warning: Missing required youth information: {', '.join(missing_fields)}"
        })

    # Calculate and store age if DOB provided
    if youth_info.get("date_of_birth"):
        age = calculate_age(youth_info["date_of_birth"])
        if age >= 0:
            youth_info["age"] = age

    # Update state
    state["youth_info"] = youth_info
    state["current_phase"] = IntakePhase.QUESTIONING.value

    # Add intake initialization message
    state["messages"].append({
        "role": "system",
        "content": f"Case {state['case_id']} initialized. Beginning structured questioning."
    })

    # Mark demographics as covered if basic info provided
    if youth_info.get("name") and youth_info.get("date_of_birth"):
        if "demographics" not in state["covered_topics"]:
            state["covered_topics"].append("demographics")
        if "demographics" in state["uncovered_topics"]:
            state["uncovered_topics"].remove("demographics")

    return state


def create_intake_summary(state: IntakeState) -> str:
    """
    Create a summary of the intake information collected.

    Args:
        state: Current intake state

    Returns:
        Formatted summary string
    """
    youth = state.get("youth_info", {})
    guardian = state.get("guardian_info", {})
    referral = state.get("referral_info", {})

    lines = [
        "=== INTAKE SUMMARY ===",
        f"Case ID: {state.get('case_id', 'N/A')}",
        f"Date: {state.get('timestamp', 'N/A')}",
        f"Officer: {state.get('intake_officer', 'N/A')}",
        "",
        "--- Youth Information ---",
        f"Name: {youth.get('name', 'N/A')}",
        f"DOB: {youth.get('date_of_birth', 'N/A')}",
        f"Age: {youth.get('age', 'N/A')}",
        f"Gender: {youth.get('gender', 'N/A')}",
        "",
        "--- Guardian Information ---",
        f"Name: {guardian.get('name', 'N/A')}",
        f"Relationship: {guardian.get('relationship', 'N/A')}",
        f"Contact: {guardian.get('phone', 'N/A')}",
        "",
        "--- Referral Information ---",
        f"Source: {referral.get('source', 'N/A')}",
        f"Reason: {referral.get('reason', 'N/A')}",
        f"Date: {referral.get('date', 'N/A')}",
    ]

    return "\n".join(lines)
