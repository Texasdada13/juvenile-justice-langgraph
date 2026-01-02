"""
Case Summary Generator Node

Synthesizes all collected information into a comprehensive case summary
with policy citations throughout.
"""

from typing import Dict, Any, List
from datetime import datetime
from ..state import IntakeState, IntakePhase


def summary_node(state: IntakeState) -> IntakeState:
    """
    Case Summary Generator Node.

    This node:
    1. Synthesizes all collected information
    2. Creates structured case summary
    3. Adds policy citations throughout
    4. Generates recommendations

    Args:
        state: Current intake state

    Returns:
        Updated state with case summary
    """
    # Update phase
    state["current_phase"] = IntakePhase.SUMMARY.value

    # Generate the case summary
    summary = generate_case_summary(state)
    state["case_summary"] = summary

    # Generate recommendations
    recommendations = generate_recommendations(state)
    state["recommendations"] = recommendations

    state["messages"].append({
        "role": "system",
        "content": "Case summary generated. Ready for officer review."
    })

    # Move to human review
    state["current_phase"] = IntakePhase.REVIEW.value

    return state


def generate_case_summary(state: IntakeState) -> str:
    """
    Generate a comprehensive case summary from all collected data.

    Args:
        state: Current intake state

    Returns:
        Formatted case summary
    """
    youth = state.get("youth_info", {})
    guardian = state.get("guardian_info", {})
    referral = state.get("referral_info", {})
    responses = state.get("responses", [])
    risk_assessment = state.get("risk_assessment", {})
    eligibility_results = state.get("eligibility_results", [])

    lines = []

    # Header
    lines.extend([
        "=" * 60,
        "JUVENILE JUSTICE INTAKE CASE SUMMARY",
        "=" * 60,
        "",
        f"Case ID: {state.get('case_id', 'N/A')}",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Intake Officer: {state.get('intake_officer', 'N/A')}",
        "",
    ])

    # Section 1: Identifying Information
    lines.extend([
        "-" * 40,
        "1. IDENTIFYING INFORMATION",
        "-" * 40,
        f"Youth Name: {youth.get('name', 'N/A')}",
        f"Date of Birth: {youth.get('date_of_birth', 'N/A')}",
        f"Age: {youth.get('age', 'N/A')}",
        f"Gender: {youth.get('gender', 'N/A')}",
        f"Race/Ethnicity: {youth.get('race', 'N/A')}",
        "",
        f"Guardian: {guardian.get('name', 'N/A')}",
        f"Relationship: {guardian.get('relationship', 'N/A')}",
        f"Contact: {guardian.get('phone', 'N/A')}",
        "",
    ])

    # Section 2: Referral Information
    lines.extend([
        "-" * 40,
        "2. REFERRAL REASON AND PRESENTING ISSUE",
        "-" * 40,
        f"Referral Source: {referral.get('source', 'N/A')}",
        f"Referral Date: {referral.get('date', 'N/A')}",
        f"Current Offense: {referral.get('reason', 'N/A')}",
        "",
    ])

    # Add offense details from responses if available
    offense_response = next(
        (r for r in responses if r.get("topic") == "current_offense"),
        None
    )
    if offense_response:
        lines.append(f"Offense Details: {offense_response.get('answer', 'N/A')}")
        lines.append("")

    # Section 3: Background and History
    lines.extend([
        "-" * 40,
        "3. BACKGROUND AND HISTORY",
        "-" * 40,
    ])

    # Organize responses by topic
    topic_order = [
        ("family_situation", "Family Situation"),
        ("living_situation", "Living Situation"),
        ("education", "Education"),
        ("employment", "Employment"),
        ("peer_relations", "Peer Relations"),
        ("substance_use", "Substance Use History"),
        ("mental_health", "Mental Health"),
        ("prior_offenses", "Prior History")
    ]

    for topic_key, topic_name in topic_order:
        topic_responses = [r for r in responses if r.get("topic") == topic_key]
        if topic_responses:
            lines.append(f"\n{topic_name}:")
            for resp in topic_responses:
                lines.append(f"  {resp.get('answer', 'N/A')}")

    lines.append("")

    # Section 4: Risk and Needs Assessment
    lines.extend([
        "-" * 40,
        "4. RISK AND NEEDS ASSESSMENT",
        "-" * 40,
        f"Assessment Tool: {risk_assessment.get('assessment_tool', 'N/A')}",
        f"(Citation: {risk_assessment.get('citation', 'N/A')})",
        "",
        f"OVERALL RISK LEVEL: {risk_assessment.get('risk_level', 'N/A').upper()}",
        f"Risk Score: {risk_assessment.get('risk_score', 0):.1f}/100",
        "",
        "Risk Factors Identified:",
    ])

    for factor in risk_assessment.get("risk_factors", []):
        lines.append(f"  - [{factor['severity'].upper()}] {factor['domain']}: {factor['factor']}")

    lines.append("\nProtective Factors:")
    for factor in risk_assessment.get("protective_factors", []):
        lines.append(f"  - {factor['type']}: {factor['indicator']}")

    lines.append("")

    # Section 5: Program Eligibility
    lines.extend([
        "-" * 40,
        "5. ELIGIBILITY FOR PROGRAMS/SERVICES",
        "-" * 40,
    ])

    for result in eligibility_results:
        status_marker = {
            "eligible": "[ELIGIBLE]",
            "ineligible": "[INELIGIBLE]",
            "conditional": "[CONDITIONAL]"
        }.get(result.get("status", ""), "[?]")

        lines.append(f"\n{status_marker} {result.get('program_name', 'N/A')}")
        lines.append(f"   Citation: {result.get('policy_citation', 'N/A')}")

        if result.get("barriers"):
            lines.append("   Barriers:")
            for barrier in result["barriers"]:
                lines.append(f"     - {barrier}")

    lines.append("")

    # Section 6: Recommendations
    lines.extend([
        "-" * 40,
        "6. RECOMMENDED NEXT STEPS",
        "-" * 40,
    ])

    for i, rec in enumerate(state.get("recommendations", []), 1):
        lines.append(f"  {i}. {rec}")

    lines.extend([
        "",
        "-" * 40,
        "7. CITATIONS AND REFERENCES",
        "-" * 40,
    ])

    # Collect all citations
    citations = set()
    for result in eligibility_results:
        if result.get("policy_citation"):
            citations.add(result["policy_citation"])
    if risk_assessment.get("citation"):
        citations.add(risk_assessment["citation"])

    for citation in sorted(citations):
        lines.append(f"  - {citation}")

    lines.extend([
        "",
        "=" * 60,
        "END OF CASE SUMMARY",
        "=" * 60,
    ])

    return "\n".join(lines)


def generate_recommendations(state: IntakeState) -> List[str]:
    """
    Generate recommendations based on assessment results.

    Args:
        state: Current intake state

    Returns:
        List of recommendations
    """
    recommendations = []
    risk_level = state.get("risk_level", "")
    eligibility_results = state.get("eligibility_results", [])
    risk_factors = state.get("risk_factors", [])

    # Recommend eligible programs
    eligible_programs = [
        r for r in eligibility_results
        if r.get("status") == "eligible"
    ]

    if eligible_programs:
        for program in eligible_programs[:3]:  # Top 3
            recommendations.append(
                f"Refer to {program['program_name']} "
                f"(per {program['policy_citation']})"
            )

    # Risk-based recommendations
    if risk_level == "very_high":
        recommendations.append(
            "Schedule immediate case conference due to elevated risk level"
        )
        recommendations.append(
            "Consider intensive supervision or secure placement evaluation"
        )
    elif risk_level == "high":
        recommendations.append(
            "Prioritize services addressing highest-risk domains"
        )
        recommendations.append(
            "Weekly check-ins recommended during initial supervision period"
        )
    elif risk_level == "moderate":
        recommendations.append(
            "Standard probation supervision with targeted services"
        )
    else:  # low
        recommendations.append(
            "Consider diversion options if eligible"
        )
        recommendations.append(
            "Minimal intervention approach recommended"
        )

    # Address specific risk factors
    domains_needing_attention = set(f["domain"] for f in risk_factors if f.get("severity") == "high")

    if "substance_abuse" in domains_needing_attention:
        recommendations.append(
            "Substance abuse assessment and treatment referral"
        )

    if "family_circumstances" in domains_needing_attention:
        recommendations.append(
            "Family therapy or parenting support services"
        )

    if "education_employment" in domains_needing_attention:
        recommendations.append(
            "Educational support and tutoring services"
        )

    if "peer_relations" in domains_needing_attention:
        recommendations.append(
            "Mentoring program to develop prosocial connections"
        )

    return recommendations
