from datetime import datetime, timezone

from app.models.hitl_decision import (
    HITLDecision,
    HITLDecisionType,
)


def test_approve_decision():
    timestamp = datetime.now(timezone.utc)

    decision = HITLDecision(
        decision=HITLDecisionType.APPROVE,
        reviewer="reviewer-001",
        comment="Commercial approval confirmed.",
        timestamp=timestamp,
    )

    assert (
        decision.decision
        == HITLDecisionType.APPROVE
    )

    assert (
        decision.reviewer
        == "reviewer-001"
    )

    assert (
        decision.comment
        == "Commercial approval confirmed."
    )

    assert decision.timestamp == timestamp


def test_reject_decision():
    timestamp = datetime.now(timezone.utc)

    decision = HITLDecision(
        decision=HITLDecisionType.REJECT,
        reviewer="reviewer-002",
        comment="Invoice price is not acceptable.",
        timestamp=timestamp,
    )

    assert (
        decision.decision
        == HITLDecisionType.REJECT
    )

    assert (
        decision.reviewer
        == "reviewer-002"
    )

    assert (
        decision.comment
        == "Invoice price is not acceptable."
    )

    assert decision.timestamp == timestamp


def test_override_decision():
    timestamp = datetime.now(timezone.utc)

    decision = HITLDecision(
        decision=HITLDecisionType.OVERRIDE,
        reviewer="reviewer-003",
        comment="Approved based on commercial exception.",
        timestamp=timestamp,
    )

    assert (
        decision.decision
        == HITLDecisionType.OVERRIDE
    )

    assert (
        decision.reviewer
        == "reviewer-003"
    )

    assert (
        decision.comment
        == "Approved based on commercial exception."
    )

    assert decision.timestamp == timestamp