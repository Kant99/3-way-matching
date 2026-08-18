from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from app.models.validation_result import ValidationResult
from app.models.hitl_decision import HITLDecision


class HITLCaseStatus(str, Enum):
    PENDING = "PENDING"
    REVIEWED = "REVIEWED"


@dataclass
class HITLCase:
    """
    Represents a Human-in-the-Loop review case.

    A HITL case is created when deterministic validation
    produces one or more exceptions.

    The case remains PENDING until a human reviewer submits
    a valid HITLDecision.
    """

    case_id: str
    status: HITLCaseStatus
    validation_result: ValidationResult
    created_at: datetime

    reviewer: Optional[str] = None

    evidence: List[Dict[str, Any]] = field(
        default_factory=list
    )

    decision: Optional[HITLDecision] = None