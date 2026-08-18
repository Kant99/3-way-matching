from datetime import datetime, timezone

import pytest

from app.capabilities.hitl_decision import (
    HITLDecisionCapability,
)
from app.models.hitl_case import (
    HITLCase,
    HITLCaseStatus,
)
from app.models.hitl_decision import (
    HITLDecision,
    HITLDecisionType,
)
from app.models.validation_result import (
    ValidationException,
    ValidationResult,
)


def create_hitl_case():
    exception = ValidationException(
        type="PRICE_MISMATCH",
        item_code="ITM-001",
        field="unit_price",
        expected=250.0,
        actual=260.0,
        tolerance="±2%",
    )

    validation_result = ValidationResult(
        status="EXCEPTION",
        exceptions=[exception],
    )

    return HITLCase(
        case_id="HITL-TEST001",
        status=HITLCaseStatus.PENDING,
        validation_result=validation_result,
        created_at=datetime.now(
            timezone.utc
        ),
        evidence=[
            {
                "document_path": (
                    "invoice_INV-2026-5001.pdf"
                ),
                "field": "whole_row",
                "page_number": 1,
                "snip_path": (
                    "outputs/evidence/"
                    "invoice_ITM-001_whole_row.png"
                ),
            }
        ],
    )


def create_decision(
    decision_type=HITLDecisionType.APPROVE,
):
    return HITLDecision(
        decision=decision_type,
        reviewer="reviewer-001",
        comment="Reviewed by human.",
        timestamp=datetime.now(
            timezone.utc
        ),
    )


def test_approve_changes_case_to_reviewed():

    hitl_case = create_hitl_case()

    decision = create_decision(
        HITLDecisionType.APPROVE
    )

    capability = HITLDecisionCapability()

    result = capability.apply(
        hitl_case,
        decision,
    )

    assert result is hitl_case

    assert (
        result.status
        == HITLCaseStatus.REVIEWED
    )

    assert result.decision is decision

    assert (
        result.reviewer
        == "reviewer-001"
    )


def test_reject_changes_case_to_reviewed():

    hitl_case = create_hitl_case()

    decision = create_decision(
        HITLDecisionType.REJECT
    )

    capability = HITLDecisionCapability()

    result = capability.apply(
        hitl_case,
        decision,
    )

    assert (
        result.status
        == HITLCaseStatus.REVIEWED
    )

    assert (
        result.decision.decision
        == HITLDecisionType.REJECT
    )


def test_override_changes_case_to_reviewed():

    hitl_case = create_hitl_case()

    decision = create_decision(
        HITLDecisionType.OVERRIDE
    )

    capability = HITLDecisionCapability()

    result = capability.apply(
        hitl_case,
        decision,
    )

    assert (
        result.status
        == HITLCaseStatus.REVIEWED
    )

    assert (
        result.decision.decision
        == HITLDecisionType.OVERRIDE
    )


def test_evidence_is_preserved():

    hitl_case = create_hitl_case()

    original_evidence = (
        hitl_case.evidence
    )

    decision = create_decision()

    capability = HITLDecisionCapability()

    result = capability.apply(
        hitl_case,
        decision,
    )

    assert (
        result.evidence
        == original_evidence
    )

    assert len(
        result.evidence
    ) == 1

    assert (
        result.evidence[0]["field"]
        == "whole_row"
    )


def test_validation_result_is_preserved():

    hitl_case = create_hitl_case()

    original_result = (
        hitl_case.validation_result
    )

    decision = create_decision()

    capability = HITLDecisionCapability()

    result = capability.apply(
        hitl_case,
        decision,
    )

    assert (
        result.validation_result
        is original_result
    )


def test_reviewer_is_taken_from_decision():

    hitl_case = create_hitl_case()

    decision = HITLDecision(
        decision=HITLDecisionType.APPROVE,
        reviewer="human-reviewer-123",
        comment="Approved.",
        timestamp=datetime.now(
            timezone.utc
        ),
    )

    capability = HITLDecisionCapability()

    result = capability.apply(
        hitl_case,
        decision,
    )

    assert (
        result.reviewer
        == "human-reviewer-123"
    )


def test_pending_case_can_be_decided_only_once():

    hitl_case = create_hitl_case()

    first_decision = create_decision(
        HITLDecisionType.APPROVE
    )

    second_decision = create_decision(
        HITLDecisionType.REJECT
    )

    capability = HITLDecisionCapability()

    capability.apply(
        hitl_case,
        first_decision,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Only PENDING HITL cases can "
            "receive a decision."
        ),
    ):
        capability.apply(
            hitl_case,
            second_decision,
        )


def test_none_case_is_rejected():

    capability = HITLDecisionCapability()

    decision = create_decision()

    with pytest.raises(
        ValueError,
        match="HITL case cannot be None.",
    ):
        capability.apply(
            None,
            decision,
        )


def test_none_decision_is_rejected():

    hitl_case = create_hitl_case()

    capability = HITLDecisionCapability()

    with pytest.raises(
        ValueError,
        match="HITL decision cannot be None.",
    ):
        capability.apply(
            hitl_case,
            None,
        )


def test_only_pending_case_can_be_decided():

    hitl_case = create_hitl_case()

    hitl_case.status = (
        HITLCaseStatus.REVIEWED
    )

    decision = create_decision()

    capability = HITLDecisionCapability()

    with pytest.raises(
        ValueError,
        match=(
            "Only PENDING HITL cases can "
            "receive a decision."
        ),
    ):
        capability.apply(
            hitl_case,
            decision,
        )