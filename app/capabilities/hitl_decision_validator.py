from app.models.hitl_decision import HITLDecision


class HITLDecisionValidator:
    """
    Validates human decisions before they are applied
    to a HITL case.

    This capability is deterministic.

    It does not create, modify, or infer decisions.
    """

    def validate(
        self,
        decision: HITLDecision,
    ) -> None:
        """
        Validate a HITL decision.

        Raises:
            ValueError: if the decision is invalid.
        """

        if decision is None:
            raise ValueError(
                "HITL decision cannot be None."
            )

        # --------------------------------------------------
        # Reviewer validation
        # --------------------------------------------------

        if not decision.reviewer:
            raise ValueError(
                "Reviewer is required."
            )

        if not decision.reviewer.strip():
            raise ValueError(
                "Reviewer cannot be empty."
            )

        # --------------------------------------------------
        # Decision validation
        # --------------------------------------------------

        if decision.decision is None:
            raise ValueError(
                "Decision type is required."
            )

        # --------------------------------------------------
        # Timestamp validation
        # --------------------------------------------------

        if decision.timestamp is None:
            raise ValueError(
                "Decision timestamp is required."
            )

        # --------------------------------------------------
        # Comment validation
        # --------------------------------------------------

        if decision.comment is not None:
            if not isinstance(
                decision.comment,
                str,
            ):
                raise ValueError(
                    "Decision comment must be a string."
                )

        # --------------------------------------------------
        # All validation passed
        # --------------------------------------------------

        return None