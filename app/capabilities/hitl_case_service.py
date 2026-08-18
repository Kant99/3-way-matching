from app.capabilities.hitl_decision import (
    HITLDecisionCapability,
)
from app.capabilities.hitl_routing import (
    HITLRoutingCapability,
)
from app.models.hitl_case import HITLCase
from app.models.hitl_decision import HITLDecision
from app.models.validation_result import (
    ValidationResult,
)
from app.repositories.hitl_case_repository import (
    HITLCaseRepository,
)


class HITLCaseService:
    """
    Coordinates the HITL case lifecycle.

    Responsibilities:

        1. Create a HITL case from a validation result.
        2. Persist the case.
        3. Retrieve an existing case.
        4. Apply a human decision.
        5. Persist the reviewed case.

    This service does not make human decisions.
    """

    def __init__(
        self,
        repository: HITLCaseRepository,
        routing_capability: (
            HITLRoutingCapability | None
        ) = None,
        decision_capability: (
            HITLDecisionCapability | None
        ) = None,
    ):
        self.repository = repository

        self.routing_capability = (
            routing_capability
            or HITLRoutingCapability()
        )

        self.decision_capability = (
            decision_capability
            or HITLDecisionCapability()
        )

    # ============================================================
    # CREATE CASE
    # ============================================================

    def create_case(
        self,
        validation_result: ValidationResult,
    ) -> HITLCase | None:
        """
        Route an exception result to HITL and persist
        the resulting case.

        Returns None when validation passed.
        """

        hitl_case = (
            self.routing_capability.route(
                validation_result
            )
        )

        if hitl_case is None:
            return None

        return self.repository.save(
            hitl_case
        )

    # ============================================================
    # GET CASE
    # ============================================================

    def get_case(
        self,
        case_id: str,
    ) -> HITLCase | None:
        """
        Retrieve an HITL case from the repository.
        """

        return self.repository.get(
            case_id
        )

    # ============================================================
    # APPLY DECISION
    # ============================================================

    def apply_decision(
        self,
        case_id: str,
        decision: HITLDecision,
    ) -> HITLCase:
        """
        Retrieve a pending HITL case, apply the supplied
        human decision, and persist the reviewed case.
        """

        hitl_case = self.repository.get(
            case_id
        )

        if hitl_case is None:
            raise ValueError(
                f"HITL case not found: "
                f"{case_id}"
            )

        reviewed_case = (
            self.decision_capability.apply(
                hitl_case,
                decision,
            )
        )

        return self.repository.update(
            reviewed_case
        )