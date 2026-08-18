from app.capabilities.hitl_decision_validator import (
    HITLDecisionValidator,
)
from app.models.hitl_case import (
    HITLCase,
    HITLCaseStatus,
)
from app.models.hitl_decision import (
    HITLDecision,
)


class HITLDecisionCapability:
    """
    Applies a validated human decision to an existing
    HITL case.

    This capability does not create or infer decisions.

    A caller must explicitly provide the human decision.
    """

    def __init__(
        self,
        validator: HITLDecisionValidator | None = None,
    ):
        self.validator = (
            validator
            or HITLDecisionValidator()
        )

    def apply(
        self,
        hitl_case: HITLCase,
        decision: HITLDecision,
    ) -> HITLCase:
        """
        Validate and apply a human decision to a HITL case.

        The case must currently be PENDING.

        A successfully applied decision changes the case
        status to REVIEWED.
        """

        if hitl_case is None:
            raise ValueError(
                "HITL case cannot be None."
            )

        if decision is None:
            raise ValueError(
                "HITL decision cannot be None."
            )

        # --------------------------------------------------
        # Case state validation
        # --------------------------------------------------

        if (
            hitl_case.status
            != HITLCaseStatus.PENDING
        ):
            raise ValueError(
                "Only PENDING HITL cases can "
                "receive a decision."
            )

        # --------------------------------------------------
        # Validate human decision
        # --------------------------------------------------

        self.validator.validate(
            decision
        )

        # --------------------------------------------------
        # Apply decision
        # --------------------------------------------------

        hitl_case.decision = decision

        hitl_case.reviewer = (
            decision.reviewer
        )

        hitl_case.status = (
            HITLCaseStatus.REVIEWED
        )

        return hitl_case