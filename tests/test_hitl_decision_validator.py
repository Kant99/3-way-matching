from datetime import datetime, timezone

import pytest

from app.capabilities.hitl_decision_validator import (
    HITLDecisionValidator,
)
from app.models.hitl_decision import (
    HITLDecision,
    HITLDecisionType,
)


def create_valid_decision(
    decision_type=HITLDecisionType.APPROVE,
):
    return HITLDecision(
        decision=decision_type,
        reviewer="reviewer-001",
        comment="Decision reviewed.",
        timestamp=datetime.now(
            timezone.utc
        ),
    )


def test_valid_approve_decision():
    decision = create_valid_decision(
        HITLDecisionType.APPROVE
    )

    validator = HITLDecisionValidator()

    result = validator.validate(
        decision
    )

    assert result is None


def test_valid_reject_decision():
    decision = create_valid_decision(
        HITLDecisionType.REJECT
    )

    validator = HITLDecisionValidator()

    result = validator.validate(
        decision
    )

    assert result is None


def test_valid_override_decision():
    decision = create_valid_decision(
        HITLDecisionType.OVERRIDE
    )

    validator = HITLDecisionValidator()

    result = validator.validate(
        decision
    )

    assert result is None


def test_reviewer_is_required():
    decision = HITLDecision(
        decision=HITLDecisionType.APPROVE,
        reviewer="",
        comment="Approved.",
        timestamp=datetime.now(
            timezone.utc
        ),
    )

    validator = HITLDecisionValidator()

    with pytest.raises(
        ValueError,
        match="Reviewer is required.",
    ):
        validator.validate(
            decision
        )


def test_reviewer_cannot_be_whitespace():
    decision = HITLDecision(
        decision=HITLDecisionType.APPROVE,
        reviewer="   ",
        comment="Approved.",
        timestamp=datetime.now(
            timezone.utc
        ),
    )

    validator = HITLDecisionValidator()

    with pytest.raises(
        ValueError,
        match="Reviewer cannot be empty.",
    ):
        validator.validate(
            decision
        )


def test_decision_type_is_required():
    decision = HITLDecision(
        decision=None,
        reviewer="reviewer-001",
        comment="Approved.",
        timestamp=datetime.now(
            timezone.utc
        ),
    )

    validator = HITLDecisionValidator()

    with pytest.raises(
        ValueError,
        match="Decision type is required.",
    ):
        validator.validate(
            decision
        )


def test_timestamp_is_required():
    decision = HITLDecision(
        decision=HITLDecisionType.APPROVE,
        reviewer="reviewer-001",
        comment="Approved.",
        timestamp=None,
    )

    validator = HITLDecisionValidator()

    with pytest.raises(
        ValueError,
        match="Decision timestamp is required.",
    ):
        validator.validate(
            decision
        )


def test_comment_is_optional():
    decision = HITLDecision(
        decision=HITLDecisionType.APPROVE,
        reviewer="reviewer-001",
        comment=None,
        timestamp=datetime.now(
            timezone.utc
        ),
    )

    validator = HITLDecisionValidator()

    result = validator.validate(
        decision
    )

    assert result is None


def test_comment_must_be_string():
    decision = HITLDecision(
        decision=HITLDecisionType.APPROVE,
        reviewer="reviewer-001",
        comment=123,
        timestamp=datetime.now(
            timezone.utc
        ),
    )

    validator = HITLDecisionValidator()

    with pytest.raises(
        ValueError,
        match="Decision comment must be a string.",
    ):
        validator.validate(
            decision
        )


def test_none_decision_is_rejected():
    validator = HITLDecisionValidator()

    with pytest.raises(
        ValueError,
        match="HITL decision cannot be None.",
    ):
        validator.validate(
            None
        )