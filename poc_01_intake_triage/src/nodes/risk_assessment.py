"""
Risk Assessment Agent Node

Evaluates risk factors, applies validated risk tools, and generates
risk summary with citations.
"""

from typing import Dict, Any, List
from ..state import IntakeState, IntakePhase, RiskFactor, RiskLevel


# Risk domains based on YLS/CMI (Youth Level of Service/Case Management Inventory)
RISK_DOMAINS = {
    "prior_offenses": {
        "weight": 2.0,
        "indicators": {
            "high": ["multiple priors", "violent history", "detention history"],
            "moderate": ["one prior", "probation history"],
            "low": ["no priors", "first offense"]
        }
    },
    "family_circumstances": {
        "weight": 1.5,
        "indicators": {
            "high": ["abuse", "neglect", "domestic violence", "incarcerated parent"],
            "moderate": ["divorce", "conflict", "absent parent", "unstable"],
            "low": ["supportive", "stable", "involved"]
        }
    },
    "education_employment": {
        "weight": 1.5,
        "indicators": {
            "high": ["expelled", "dropped out", "severe truancy"],
            "moderate": ["suspended", "failing", "truancy", "disengaged"],
            "low": ["enrolled", "passing", "engaged", "employed"]
        }
    },
    "peer_relations": {
        "weight": 1.5,
        "indicators": {
            "high": ["gang involvement", "all delinquent peers"],
            "moderate": ["some delinquent peers", "few friends"],
            "low": ["prosocial peers", "positive friends"]
        }
    },
    "substance_abuse": {
        "weight": 1.5,
        "indicators": {
            "high": ["daily use", "addiction", "multiple substances"],
            "moderate": ["occasional use", "experimental"],
            "low": ["no use", "never tried"]
        }
    },
    "leisure_recreation": {
        "weight": 1.0,
        "indicators": {
            "high": ["no activities", "unstructured time", "negative activities"],
            "moderate": ["limited activities", "inconsistent involvement"],
            "low": ["organized activities", "sports", "hobbies", "positive interests"]
        }
    },
    "personality_behavior": {
        "weight": 1.5,
        "indicators": {
            "high": ["aggressive", "impulsive", "callous", "anger issues"],
            "moderate": ["some impulsivity", "occasional outbursts"],
            "low": ["self-control", "empathy", "regret"]
        }
    },
    "attitudes": {
        "weight": 1.0,
        "indicators": {
            "high": ["antisocial attitudes", "no remorse", "pro-criminal"],
            "moderate": ["minimizes offense", "blames others"],
            "low": ["takes responsibility", "remorseful", "prosocial values"]
        }
    }
}

# Protective factors
PROTECTIVE_FACTORS = {
    "family_support": ["supportive family", "involved parent", "strong bond"],
    "school_engagement": ["enrolled", "passing", "likes school", "good grades"],
    "prosocial_activities": ["sports", "clubs", "church", "volunteering"],
    "positive_peers": ["prosocial friends", "positive influences"],
    "future_orientation": ["goals", "plans", "motivated", "hopeful"],
    "mentor_relationship": ["mentor", "coach", "positive adult"]
}


def extract_risk_factors(state: IntakeState) -> List[RiskFactor]:
    """
    Extract risk factors from interview responses.

    Args:
        state: Current intake state

    Returns:
        List of identified risk factors
    """
    risk_factors = []
    responses = state.get("responses", [])

    for qa in responses:
        topic = qa.get("topic", "")
        answer = qa.get("answer", "").lower()

        # Map topics to risk domains
        domain_mapping = {
            "prior_offenses": "prior_offenses",
            "current_offense": "prior_offenses",
            "family_situation": "family_circumstances",
            "education": "education_employment",
            "employment": "education_employment",
            "peer_relations": "peer_relations",
            "substance_use": "substance_abuse",
            "mental_health": "personality_behavior",
            "strengths_protective_factors": None  # Handled separately
        }

        domain = domain_mapping.get(topic)
        if not domain:
            continue

        domain_info = RISK_DOMAINS.get(domain, {})
        indicators = domain_info.get("indicators", {})

        # Check for high-risk indicators
        for level in ["high", "moderate", "low"]:
            level_indicators = indicators.get(level, [])
            for indicator in level_indicators:
                if indicator in answer:
                    risk_factors.append({
                        "domain": domain,
                        "factor": indicator,
                        "evidence": answer[:200],
                        "source": f"Intake interview - {topic}",
                        "severity": level
                    })
                    break  # Only one factor per domain for now

    return risk_factors


def extract_protective_factors(state: IntakeState) -> List[Dict[str, Any]]:
    """
    Extract protective factors from interview responses.

    Args:
        state: Current intake state

    Returns:
        List of identified protective factors
    """
    protective = []
    responses = state.get("responses", [])

    for qa in responses:
        answer = qa.get("answer", "").lower()

        for factor_type, indicators in PROTECTIVE_FACTORS.items():
            for indicator in indicators:
                if indicator in answer:
                    protective.append({
                        "type": factor_type,
                        "indicator": indicator,
                        "evidence": answer[:200],
                        "source": f"Intake interview - {qa.get('topic', '')}"
                    })
                    break

    return protective


def calculate_risk_score(risk_factors: List[RiskFactor]) -> tuple[float, str]:
    """
    Calculate overall risk score based on identified factors.

    Args:
        risk_factors: List of risk factors

    Returns:
        Tuple of (score, risk_level)
    """
    total_score = 0.0
    max_possible = sum(d["weight"] * 3 for d in RISK_DOMAINS.values())  # 3 = max severity

    severity_scores = {"high": 3, "moderate": 2, "low": 1}

    for factor in risk_factors:
        domain = factor.get("domain", "")
        severity = factor.get("severity", "low")

        domain_weight = RISK_DOMAINS.get(domain, {}).get("weight", 1.0)
        severity_score = severity_scores.get(severity, 1)

        total_score += domain_weight * severity_score

    # Normalize to 0-100
    normalized_score = (total_score / max_possible) * 100 if max_possible > 0 else 0

    # Determine risk level
    if normalized_score >= 70:
        risk_level = RiskLevel.VERY_HIGH.value
    elif normalized_score >= 50:
        risk_level = RiskLevel.HIGH.value
    elif normalized_score >= 30:
        risk_level = RiskLevel.MODERATE.value
    else:
        risk_level = RiskLevel.LOW.value

    return normalized_score, risk_level


def risk_assessment_node(state: IntakeState) -> IntakeState:
    """
    Risk Assessment Agent Node.

    This node:
    1. Extracts risk factors from responses
    2. Identifies protective factors
    3. Calculates risk score
    4. Generates risk summary with citations

    Args:
        state: Current intake state

    Returns:
        Updated state with risk assessment
    """
    # Update phase
    state["current_phase"] = IntakePhase.RISK_ASSESSMENT.value

    # Extract risk factors
    risk_factors = extract_risk_factors(state)
    state["risk_factors"] = risk_factors

    # Extract protective factors
    protective_factors = extract_protective_factors(state)

    # Calculate risk score
    risk_score, risk_level = calculate_risk_score(risk_factors)
    state["risk_level"] = risk_level

    # Build risk assessment summary
    state["risk_assessment"] = {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "protective_factors": protective_factors,
        "domains_assessed": list(RISK_DOMAINS.keys()),
        "assessment_tool": "YLS/CMI-Based Assessment",
        "citation": "Risk Assessment Policy, Section 2.1"
    }

    state["messages"].append({
        "role": "system",
        "content": f"Risk assessment complete. Risk level: {risk_level.upper()} (Score: {risk_score:.1f})"
    })

    # Move to summary generation
    state["current_phase"] = IntakePhase.SUMMARY.value

    return state


def format_risk_report(assessment: Dict[str, Any]) -> str:
    """
    Format risk assessment into a readable report.

    Args:
        assessment: Risk assessment dictionary

    Returns:
        Formatted report string
    """
    lines = [
        "=== RISK ASSESSMENT REPORT ===",
        f"Assessment Tool: {assessment.get('assessment_tool', 'N/A')}",
        f"Citation: {assessment.get('citation', 'N/A')}",
        "",
        f"OVERALL RISK LEVEL: {assessment.get('risk_level', 'N/A').upper()}",
        f"Risk Score: {assessment.get('risk_score', 0):.1f}/100",
        "",
        "--- Risk Factors Identified ---"
    ]

    for factor in assessment.get("risk_factors", []):
        lines.append(f"  [{factor['severity'].upper()}] {factor['domain']}: {factor['factor']}")
        lines.append(f"      Evidence: {factor['evidence'][:100]}...")

    lines.append("")
    lines.append("--- Protective Factors ---")

    for factor in assessment.get("protective_factors", []):
        lines.append(f"  [+] {factor['type']}: {factor['indicator']}")

    return "\n".join(lines)
