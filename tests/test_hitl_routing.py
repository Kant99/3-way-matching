from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from app.models.hitl_case import (
    HITLCase,
    HITLCaseStatus,
)
from app.models.validation_result import (
    ValidationResult,
)


class HITLRoutingCapability:
    """
    Routes validation exceptions to Human-in-the-Loop.

    MatchingEngine is responsible for deterministic validation
    and evidence generation.

    This capability creates the HITL case and carries the
    already-generated evidence from the ValidationExceptions.
    """

    def route(
        self,
        validation_result: ValidationResult,
        evidence: List[Dict[str, Any]] | None = None,
    ) -> HITLCase | None:
        """
        Create a HITL case when validation produces exceptions.

        If evidence is explicitly supplied, use it.

        Otherwise, collect evidence directly from the
        ValidationException objects.
        """

        # --------------------------------------------------
        # 1. Only EXCEPTION results go to HITL
        # --------------------------------------------------

        if validation_result.status != "EXCEPTION":
            return None

        # --------------------------------------------------
        # 2. EXCEPTION must contain exceptions
        # --------------------------------------------------

        if not validation_result.exceptions:
            return None

        # --------------------------------------------------
        # 3. Create HITL case ID
        # --------------------------------------------------

        case_id = (
            f"HITL-{uuid4().hex[:8].upper()}"
        )

        # --------------------------------------------------
        # 4. Collect evidence
        # --------------------------------------------------

        if evidence is None:
            evidence = []

            for exception in (
                validation_result.exceptions
            ):
                if not exception.evidence:
                    continue

                evidence.extend(
                    exception.evidence
                )

        # --------------------------------------------------
        # 5. Create HITL case
        # --------------------------------------------------

        return HITLCase(
            case_id=case_id,
            status=HITLCaseStatus.PENDING,
            validation_result=validation_result,
            created_at=datetime.now(
                timezone.utc
            ),
            reviewer=None,
            evidence=evidence,
            decision=None,
        )