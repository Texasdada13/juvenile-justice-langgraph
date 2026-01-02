"""
State schema for the Intake Triage Assistant.

Defines the TypedDict state that flows through the LangGraph pipeline.
"""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class IntakePhase(str, Enum):
    """Current phase of the intake process."""
    INTAKE = "intake"
    QUESTIONING = "questioning"
    POLICY_RETRIEVAL = "policy_retrieval"
    ELIGIBILITY = "eligibility"
    RISK_ASSESSMENT = "risk_assessment"
    SUMMARY = "summary"
    REVIEW = "review"
    COMPLETE = "complete"


class EligibilityStatus(str, Enum):
    """Eligibility determination status."""
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    CONDITIONAL = "conditional"
    PENDING = "pending"


class RiskLevel(str, Enum):
    """Risk assessment level."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class QuestionAnswer(TypedDict):
    """A question-answer pair from the intake interview."""
    question: str
    answer: str
    topic: str
    timestamp: str


class PolicyDocument(TypedDict):
    """A retrieved policy document."""
    content: str
    source: str
    section: str
    relevance_score: float
    metadata: Dict[str, Any]


class EligibilityResult(TypedDict):
    """Result of eligibility checking for a program."""
    program_name: str
    status: str  # EligibilityStatus value
    criteria_matched: List[Dict[str, Any]]
    barriers: List[str]
    policy_citation: str
    confidence: float


class RiskFactor(TypedDict):
    """An identified risk factor."""
    domain: str
    factor: str
    evidence: str
    source: str
    severity: str


class IntakeState(TypedDict):
    """
    Main state object for the Intake Triage Assistant.

    This state flows through all nodes in the LangGraph pipeline.
    """
    # Case identification
    case_id: str
    timestamp: str
    intake_officer: str

    # Youth information
    youth_info: Dict[str, Any]  # name, dob, demographics, contact
    guardian_info: Dict[str, Any]
    referral_info: Dict[str, Any]  # source, reason, date

    # Intake process tracking
    current_phase: str  # IntakePhase value
    responses: List[QuestionAnswer]
    covered_topics: List[str]
    uncovered_topics: List[str]

    # Retrieved knowledge
    retrieved_policies: List[PolicyDocument]
    similar_cases: List[Dict[str, Any]]

    # Assessments
    risk_assessment: Dict[str, Any]
    risk_factors: List[RiskFactor]
    risk_level: str  # RiskLevel value
    eligibility_results: List[EligibilityResult]

    # Output
    case_summary: str
    recommendations: List[str]

    # Human review
    officer_notes: str
    officer_edits: Dict[str, str]
    approved: bool
    request_additional_questioning: bool

    # Workflow control
    messages: List[Dict[str, str]]  # Conversation history
    error: Optional[str]


def create_initial_state(
    intake_officer: str,
    youth_info: Optional[Dict[str, Any]] = None,
    guardian_info: Optional[Dict[str, Any]] = None,
    referral_info: Optional[Dict[str, Any]] = None
) -> IntakeState:
    """
    Create an initial state for a new intake.

    Args:
        intake_officer: Name/ID of the intake officer
        youth_info: Optional pre-filled youth information
        guardian_info: Optional pre-filled guardian information
        referral_info: Optional referral information

    Returns:
        Initialized IntakeState
    """
    import uuid

    # Define required topics for comprehensive intake
    required_topics = [
        "demographics",
        "family_situation",
        "living_situation",
        "education",
        "employment",
        "mental_health",
        "substance_use",
        "peer_relations",
        "prior_offenses",
        "current_offense",
        "strengths_protective_factors"
    ]

    return IntakeState(
        # Case identification
        case_id=str(uuid.uuid4())[:8].upper(),
        timestamp=datetime.now().isoformat(),
        intake_officer=intake_officer,

        # Youth information
        youth_info=youth_info or {},
        guardian_info=guardian_info or {},
        referral_info=referral_info or {},

        # Intake process tracking
        current_phase=IntakePhase.INTAKE.value,
        responses=[],
        covered_topics=[],
        uncovered_topics=required_topics.copy(),

        # Retrieved knowledge
        retrieved_policies=[],
        similar_cases=[],

        # Assessments
        risk_assessment={},
        risk_factors=[],
        risk_level=RiskLevel.PENDING.value if hasattr(RiskLevel, 'PENDING') else "",
        eligibility_results=[],

        # Output
        case_summary="",
        recommendations=[],

        # Human review
        officer_notes="",
        officer_edits={},
        approved=False,
        request_additional_questioning=False,

        # Workflow control
        messages=[],
        error=None
    )
