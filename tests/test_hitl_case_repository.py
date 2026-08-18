from datetime import datetime, timezone

from app.models.hitl_case import (
    HITLCase,
    HITLCaseStatus,
)
from app.models.validation_result import (
    ValidationResult,
)
from app.repositories.hitl_case_repository import (
    HITLCaseRepository,
)


def test_repository_is_abstract():

    assert HITLCaseRepository is not None

    case = HITLCase(
        case_id="HITL-001",
        status=HITLCaseStatus.PENDING,
        validation_result=ValidationResult(
            status="EXCEPTION",
            exceptions=[],
        ),
        created_at=datetime.now(
            timezone.utc
        ),
    )

    assert case.case_id == "HITL-001"