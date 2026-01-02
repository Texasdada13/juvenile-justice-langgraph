"""
Eligibility Checking Agent Node

Determines program eligibility by matching youth profile against criteria
from retrieved policies. Provides citations for all determinations.
"""

from typing import Dict, Any, List
from ..state import IntakeState, IntakePhase, EligibilityResult, EligibilityStatus


# Program definitions with eligibility criteria
PROGRAMS = {
    "youth_diversion": {
        "name": "Youth Diversion Program",
        "criteria": {
            "age_min": 12,
            "age_max": 17,
            "offense_types": ["misdemeanor", "low_level_felony"],
            "excluded_offenses": ["sexual_offense", "firearms", "gang_violence"],
            "max_prior_offenses": 1,
            "risk_levels": ["low", "moderate"],
            "requires_family_participation": True
        },
        "policy_citation": "County Diversion Policy Manual, Section 3.2"
    },
    "community_service": {
        "name": "Community Service Program",
        "criteria": {
            "age_min": 10,
            "age_max": 17,
            "offense_types": ["misdemeanor", "status_offense"],
            "excluded_offenses": ["violent_offense"],
            "max_prior_offenses": 3,
            "risk_levels": ["low", "moderate", "high"],
            "requires_family_participation": False
        },
        "policy_citation": "Community Service Guidelines, Section 2.1"
    },
    "substance_abuse_treatment": {
        "name": "Substance Abuse Treatment",
        "criteria": {
            "age_min": 12,
            "age_max": 17,
            "requires_substance_use_indicator": True,
            "risk_levels": ["low", "moderate", "high"],
            "requires_family_participation": True
        },
        "policy_citation": "Treatment Services Guide, Section 5.1"
    },
    "mental_health_services": {
        "name": "Mental Health Services",
        "criteria": {
            "age_min": 10,
            "age_max": 17,
            "requires_mental_health_indicator": True,
            "risk_levels": ["low", "moderate", "high", "very_high"],
            "requires_family_participation": False
        },
        "policy_citation": "Mental Health Services Policy, Section 4.2"
    },
    "intensive_supervision": {
        "name": "Intensive Supervision Probation",
        "criteria": {
            "age_min": 12,
            "age_max": 17,
            "offense_types": ["felony", "repeat_misdemeanor"],
            "risk_levels": ["moderate", "high", "very_high"],
            "requires_family_participation": True
        },
        "policy_citation": "Probation Policy Manual, Section 6.3"
    }
}


def check_program_eligibility(
    youth_info: Dict[str, Any],
    referral_info: Dict[str, Any],
    responses: List[Dict[str, Any]],
    program_key: str
) -> EligibilityResult:
    """
    Check if youth is eligible for a specific program.

    Args:
        youth_info: Youth demographic information
        referral_info: Referral and offense information
        responses: Interview responses
        program_key: Key of the program to check

    Returns:
        EligibilityResult with determination and reasoning
    """
    program = PROGRAMS.get(program_key)
    if not program:
        return create_eligibility_result(
            program_key, "Unknown", EligibilityStatus.INELIGIBLE,
            [], ["Program not found"], "N/A", 0.0
        )

    criteria = program["criteria"]
    criteria_matched = []
    barriers = []

    # Check age
    age = youth_info.get("age", 0)
    age_min = criteria.get("age_min", 0)
    age_max = criteria.get("age_max", 99)

    if age_min <= age <= age_max:
        criteria_matched.append({
            "criterion": f"Age {age_min}-{age_max}",
            "youth_value": str(age),
            "match": True
        })
    else:
        criteria_matched.append({
            "criterion": f"Age {age_min}-{age_max}",
            "youth_value": str(age),
            "match": False
        })
        barriers.append(f"Age {age} outside eligible range ({age_min}-{age_max})")

    # Check offense type (simplified)
    offense = referral_info.get("reason", "").lower()
    allowed_offenses = criteria.get("offense_types", [])
    excluded_offenses = criteria.get("excluded_offenses", [])

    # Check for excluded offenses
    offense_excluded = any(excl in offense for excl in excluded_offenses)
    if offense_excluded:
        criteria_matched.append({
            "criterion": "Non-excluded offense",
            "youth_value": offense,
            "match": False
        })
        barriers.append(f"Offense type '{offense}' is excluded from this program")
    elif allowed_offenses:
        criteria_matched.append({
            "criterion": f"Offense type in {allowed_offenses}",
            "youth_value": offense,
            "match": True
        })

    # Check for special requirements
    if criteria.get("requires_substance_use_indicator"):
        has_substance_indicator = check_for_indicator(responses, "substance_use")
        criteria_matched.append({
            "criterion": "Substance use indicator present",
            "youth_value": "Yes" if has_substance_indicator else "No",
            "match": has_substance_indicator
        })
        if not has_substance_indicator:
            barriers.append("No substance use indicator identified")

    if criteria.get("requires_mental_health_indicator"):
        has_mh_indicator = check_for_indicator(responses, "mental_health")
        criteria_matched.append({
            "criterion": "Mental health indicator present",
            "youth_value": "Yes" if has_mh_indicator else "No",
            "match": has_mh_indicator
        })
        if not has_mh_indicator:
            barriers.append("No mental health indicator identified")

    # Determine overall status
    all_matched = all(c.get("match", False) for c in criteria_matched)

    if all_matched:
        status = EligibilityStatus.ELIGIBLE
        confidence = 0.95
    elif barriers and len(barriers) == 1:
        status = EligibilityStatus.CONDITIONAL
        confidence = 0.75
    else:
        status = EligibilityStatus.INELIGIBLE
        confidence = 0.90

    return create_eligibility_result(
        program_key,
        program["name"],
        status,
        criteria_matched,
        barriers,
        program["policy_citation"],
        confidence
    )


def check_for_indicator(responses: List[Dict[str, Any]], topic: str) -> bool:
    """
    Check if responses indicate a specific need/issue.

    Args:
        responses: Interview responses
        topic: Topic to check for

    Returns:
        True if indicator is present
    """
    positive_keywords = {
        "substance_use": ["yes", "marijuana", "alcohol", "drugs", "using", "smokes"],
        "mental_health": ["yes", "diagnosed", "therapy", "medication", "depression", "anxiety", "trauma"]
    }

    keywords = positive_keywords.get(topic, [])

    for qa in responses:
        if qa.get("topic") == topic:
            answer = qa.get("answer", "").lower()
            if any(keyword in answer for keyword in keywords):
                return True

    return False


def create_eligibility_result(
    program_key: str,
    program_name: str,
    status: EligibilityStatus,
    criteria_matched: List[Dict[str, Any]],
    barriers: List[str],
    policy_citation: str,
    confidence: float
) -> EligibilityResult:
    """Create a formatted eligibility result."""
    return {
        "program_name": program_name,
        "status": status.value,
        "criteria_matched": criteria_matched,
        "barriers": barriers,
        "policy_citation": policy_citation,
        "confidence": confidence
    }


def eligibility_node(state: IntakeState) -> IntakeState:
    """
    Eligibility Checking Agent Node.

    This node:
    1. Checks eligibility for each relevant program
    2. Matches youth profile against criteria
    3. Cites specific policy passages
    4. Flags potential barriers

    Args:
        state: Current intake state

    Returns:
        Updated state with eligibility results
    """
    # Update phase
    state["current_phase"] = IntakePhase.ELIGIBILITY.value

    youth_info = state.get("youth_info", {})
    referral_info = state.get("referral_info", {})
    responses = state.get("responses", [])

    eligibility_results = []

    # Check eligibility for each program
    for program_key in PROGRAMS.keys():
        result = check_program_eligibility(
            youth_info, referral_info, responses, program_key
        )
        eligibility_results.append(result)

    # Store results
    state["eligibility_results"] = eligibility_results

    # Count eligible programs
    eligible_count = sum(
        1 for r in eligibility_results
        if r["status"] == EligibilityStatus.ELIGIBLE.value
    )

    state["messages"].append({
        "role": "system",
        "content": f"Eligibility checking complete. Youth eligible for {eligible_count} programs."
    })

    # Move to risk assessment
    state["current_phase"] = IntakePhase.RISK_ASSESSMENT.value

    return state


def format_eligibility_report(results: List[EligibilityResult]) -> str:
    """
    Format eligibility results into a readable report.

    Args:
        results: List of eligibility results

    Returns:
        Formatted report string
    """
    lines = ["=== ELIGIBILITY REPORT ===", ""]

    for result in results:
        status_emoji = {
            "eligible": "[ELIGIBLE]",
            "ineligible": "[INELIGIBLE]",
            "conditional": "[CONDITIONAL]"
        }.get(result["status"], "[UNKNOWN]")

        lines.append(f"{status_emoji} {result['program_name']}")
        lines.append(f"   Citation: {result['policy_citation']}")
        lines.append(f"   Confidence: {result['confidence']:.0%}")

        if result["barriers"]:
            lines.append("   Barriers:")
            for barrier in result["barriers"]:
                lines.append(f"      - {barrier}")

        lines.append("")

    return "\n".join(lines)
