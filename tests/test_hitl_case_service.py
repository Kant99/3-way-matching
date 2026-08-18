from datetime import datetime, timezone

import pytest

from app.capabilities.hitl_case_service import (
    HITLCaseService,
)
from app.models.hitl_case import (
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
from app.repositories.in_memory_hitl_case_repository import (
    InMemoryHITLCaseRepository,
)


def create_validation_result():

    exception = ValidationException(
        type="PRICE_MISMATCH",
        item_code="ITM-001",
        field="unit_price",
        expected=250,
        actual=260,
        tolerance="±2%",
        evidence=[
            {
                "document_path": (
                    "data/invoices/"
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

    return ValidationResult(
        status="EXCEPTION",
        exceptions=[
            exception
        ],
    )


def create_service():

    repository = (
        InMemoryHITLCaseRepository()
    )

    service = HITLCaseService(
        repository=repository
    )

    return service, repository


def create_decision(
    decision_type=HITLDecisionType.APPROVE,
):

    return HITLDecision(
        decision=decision_type,
        reviewer="reviewer-001",
        comment="Human review completed.",
        timestamp=datetime.now(
            timezone.utc
        ),
    )


def test_create_case_persists_case():

    service, repository = (
        create_service()
    )

    validation_result = (
        create_validation_result()
    )

    hitl_case = service.create_case(
        validation_result
    )

    assert hitl_case is not None

    assert (
        hitl_case.status
        == HITLCaseStatus.PENDING
    )

    assert (
        hitl_case.case_id
        != ""
    )

    retrieved_case = repository.get(
        hitl_case.case_id
    )

    assert (
        retrieved_case is hitl_case
    )


def test_create_case_preserves_validation_result():

    service, repository = (
        create_service()
    )

    validation_result = (
        create_validation_result()
    )

    hitl_case = service.create_case(
        validation_result
    )

    assert hitl_case is not None

    assert (
        hitl_case.validation_result
        is validation_result
    )


def test_create_case_preserves_whole_row_evidence():

    service, repository = (
        create_service()
    )

    validation_result = (
        create_validation_result()
    )

    hitl_case = service.create_case(
        validation_result
    )

    assert hitl_case is not None

    assert hitl_case.evidence

    assert (
        len(hitl_case.evidence)
        == 1
    )

    assert (
        hitl_case.evidence[0]["field"]
        == "whole_row"
    )


def test_get_case_returns_persisted_case():

    service, repository = (
        create_service()
    )

    validation_result = (
        create_validation_result()
    )

    created_case = service.create_case(
        validation_result
    )

    retrieved_case = service.get_case(
        created_case.case_id
    )

    assert (
        retrieved_case
        is created_case
    )


def test_apply_approve_decision_persists_reviewed_case():

    service, repository = (
        create_service()
    )

    validation_result = (
        create_validation_result()
    )

    hitl_case = service.create_case(
        validation_result
    )

    decision = create_decision(
        HITLDecisionType.APPROVE
    )

    reviewed_case = (
        service.apply_decision(
            hitl_case.case_id,
            decision,
        )
    )

    assert (
        reviewed_case.status
        == HITLCaseStatus.REVIEWED
    )

    assert (
        reviewed_case.decision
        is decision
    )

    persisted_case = repository.get(
        hitl_case.case_id
    )

    assert (
        persisted_case.status
        == HITLCaseStatus.REVIEWED
    )

    assert (
        persisted_case.decision
        is decision
    )


def test_apply_reject_decision():

    service, repository = (
        create_service()
    )

    validation_result = (
        create_validation_result()
    )

    hitl_case = service.create_case(
        validation_result
    )

    decision = create_decision(
        HITLDecisionType.REJECT
    )

    reviewed_case = (
        service.apply_decision(
            hitl_case.case_id,
            decision,
        )
    )

    assert (
        reviewed_case.status
        == HITLCaseStatus.REVIEWED
    )

    assert (
        reviewed_case.decision.decision
        == HITLDecisionType.REJECT
    )


def test_apply_override_decision():

    service, repository = (
        create_service()
    )

    validation_result = (
        create_validation_result()
    )

    hitl_case = service.create_case(
        validation_result
    )

    decision = create_decision(
        HITLDecisionType.OVERRIDE
    )

    reviewed_case = (
        service.apply_decision(
            hitl_case.case_id,
            decision,
        )
    )

    assert (
        reviewed_case.status
        == HITLCaseStatus.REVIEWED
    )

    assert (
        reviewed_case.decision.decision
        == HITLDecisionType.OVERRIDE
    )


def test_apply_decision_preserves_evidence():

    service, repository = (
        create_service()
    )

    validation_result = (
        create_validation_result()
    )

    hitl_case = service.create_case(
        validation_result
    )

    original_evidence = (
        hitl_case.evidence
    )

    decision = create_decision()

    reviewed_case = (
        service.apply_decision(
            hitl_case.case_id,
            decision,
        )
    )

    assert (
        reviewed_case.evidence
        == original_evidence
    )

    assert (
        reviewed_case.evidence[0][
            "field"
        ]
        == "whole_row"
    )


def test_apply_decision_preserves_validation_result():

    service, repository = (
        create_service()
    )

    validation_result = (
        create_validation_result()
    )

    hitl_case = service.create_case(
        validation_result
    )

    decision = create_decision()

    reviewed_case = (
        service.apply_decision(
            hitl_case.case_id,
            decision,
        )
    )

    assert (
        reviewed_case.validation_result
        is validation_result
    )


def test_apply_decision_for_unknown_case_fails():

    service, repository = (
        create_service()
    )

    decision = create_decision()

    with pytest.raises(
        ValueError,
        match="HITL case not found",
    ):
        service.apply_decision(
            "HITL-DOES-NOT-EXIST",
            decision,
        )


def test_create_case_for_pass_returns_none():

    service, repository = (
        create_service()
    )

    validation_result = ValidationResult(
        status="PASS",
        exceptions=[],
    )

    result = service.create_case(
        validation_result
    )

    assert result is None