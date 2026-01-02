"""
Scoring Patterns

Lightweight scoring utilities adapted from the Universal Business Solution Framework.
Useful for risk assessment and eligibility scoring in juvenile justice contexts.
"""

from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level classifications."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class WeightedCriterion:
    """A single weighted scoring criterion."""
    name: str
    weight: float
    evaluator: Callable[[Any], float]  # Returns 0-1 score
    description: str = ""


@dataclass
class ScoringResult:
    """Result of a scoring evaluation."""
    total_score: float
    max_possible: float
    normalized_score: float  # 0-100
    criterion_scores: Dict[str, float]
    risk_level: str
    details: Dict[str, Any] = field(default_factory=dict)


class WeightedScorer:
    """
    Weighted scoring engine for risk and eligibility assessment.

    Example usage:
        scorer = WeightedScorer()
        scorer.add_criterion("prior_offenses", 2.0, lambda x: min(x / 5, 1.0))
        scorer.add_criterion("family_support", 1.5, lambda x: 1 - x)  # inverse

        result = scorer.score({
            "prior_offenses": 2,
            "family_support": 0.3
        })
    """

    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        """
        Initialize scorer.

        Args:
            thresholds: Risk level thresholds (default: 25/50/75)
        """
        self.criteria: Dict[str, WeightedCriterion] = {}
        self.thresholds = thresholds or {
            RiskLevel.LOW: 25,
            RiskLevel.MODERATE: 50,
            RiskLevel.HIGH: 75
        }

    def add_criterion(
        self,
        name: str,
        weight: float,
        evaluator: Callable[[Any], float],
        description: str = ""
    ) -> "WeightedScorer":
        """Add a scoring criterion."""
        self.criteria[name] = WeightedCriterion(
            name=name,
            weight=weight,
            evaluator=evaluator,
            description=description
        )
        return self

    def score(self, data: Dict[str, Any]) -> ScoringResult:
        """
        Calculate weighted score.

        Args:
            data: Dictionary of criterion_name -> value

        Returns:
            ScoringResult with total and breakdown
        """
        total_score = 0.0
        max_possible = 0.0
        criterion_scores = {}

        for name, criterion in self.criteria.items():
            value = data.get(name, 0)
            raw_score = criterion.evaluator(value)
            weighted_score = raw_score * criterion.weight

            criterion_scores[name] = {
                "raw_value": value,
                "raw_score": raw_score,
                "weight": criterion.weight,
                "weighted_score": weighted_score
            }

            total_score += weighted_score
            max_possible += criterion.weight

        # Normalize to 0-100
        normalized = (total_score / max_possible * 100) if max_possible > 0 else 0

        # Determine risk level
        risk_level = self._get_risk_level(normalized)

        return ScoringResult(
            total_score=total_score,
            max_possible=max_possible,
            normalized_score=normalized,
            criterion_scores=criterion_scores,
            risk_level=risk_level.value
        )

    def _get_risk_level(self, score: float) -> RiskLevel:
        """Determine risk level from normalized score."""
        if score >= self.thresholds.get(RiskLevel.HIGH, 75):
            return RiskLevel.VERY_HIGH
        elif score >= self.thresholds.get(RiskLevel.MODERATE, 50):
            return RiskLevel.HIGH
        elif score >= self.thresholds.get(RiskLevel.LOW, 25):
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW


def create_risk_scorer() -> WeightedScorer:
    """
    Create a pre-configured risk scorer for juvenile justice.

    Based on YLS/CMI risk domains.
    """
    scorer = WeightedScorer()

    # Prior and current offenses
    scorer.add_criterion(
        "prior_offenses",
        weight=2.0,
        evaluator=lambda x: min(x / 3, 1.0),  # 3+ priors = max score
        description="Number of prior offenses"
    )

    # Family circumstances
    scorer.add_criterion(
        "family_dysfunction",
        weight=1.5,
        evaluator=lambda x: x,  # 0-1 scale
        description="Level of family dysfunction"
    )

    # Education/employment
    scorer.add_criterion(
        "education_problems",
        weight=1.5,
        evaluator=lambda x: x,
        description="School disengagement/truancy"
    )

    # Peer relations
    scorer.add_criterion(
        "delinquent_peers",
        weight=1.5,
        evaluator=lambda x: x,
        description="Association with delinquent peers"
    )

    # Substance abuse
    scorer.add_criterion(
        "substance_abuse",
        weight=1.5,
        evaluator=lambda x: x,
        description="Substance use severity"
    )

    # Leisure/recreation
    scorer.add_criterion(
        "lack_prosocial",
        weight=1.0,
        evaluator=lambda x: x,
        description="Lack of prosocial activities"
    )

    # Personality/behavior
    scorer.add_criterion(
        "antisocial_behavior",
        weight=1.5,
        evaluator=lambda x: x,
        description="Antisocial attitudes/behavior"
    )

    return scorer


def create_eligibility_scorer(criteria: List[Dict[str, Any]]) -> WeightedScorer:
    """
    Create an eligibility scorer from criteria definitions.

    Args:
        criteria: List of criteria dicts with name, weight, threshold

    Returns:
        Configured WeightedScorer
    """
    scorer = WeightedScorer(thresholds={
        RiskLevel.LOW: 50,  # Below 50 = ineligible
        RiskLevel.MODERATE: 70,
        RiskLevel.HIGH: 90
    })

    for c in criteria:
        scorer.add_criterion(
            name=c["name"],
            weight=c.get("weight", 1.0),
            evaluator=c.get("evaluator", lambda x: float(bool(x))),
            description=c.get("description", "")
        )

    return scorer
