"""
Logging utilities.
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None
) -> None:
    """
    Set up logging configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        format_string: Custom format string
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class AuditLogger:
    """
    Specialized logger for audit trail events.

    Logs compliance checks, decisions, and state changes.
    """

    def __init__(self, name: str = "audit"):
        self.logger = logging.getLogger(f"audit.{name}")

    def log_action(
        self,
        action_type: str,
        case_id: str,
        user: str,
        details: dict
    ) -> None:
        """Log an action for audit trail."""
        self.logger.info(
            f"ACTION: {action_type} | Case: {case_id} | User: {user} | Details: {details}"
        )

    def log_decision(
        self,
        decision_type: str,
        case_id: str,
        result: str,
        rationale: str
    ) -> None:
        """Log a decision for audit trail."""
        self.logger.info(
            f"DECISION: {decision_type} | Case: {case_id} | Result: {result} | Rationale: {rationale}"
        )

    def log_compliance_check(
        self,
        check_type: str,
        case_id: str,
        passed: bool,
        citation: str
    ) -> None:
        """Log a compliance check."""
        status = "PASSED" if passed else "FAILED"
        self.logger.info(
            f"COMPLIANCE: {check_type} | Case: {case_id} | Status: {status} | Citation: {citation}"
        )
