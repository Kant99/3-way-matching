from datetime import datetime, timezone

import pytest

from app.models.hitl_case import (
    HITLCase,
    HITLCaseStatus,
)
from app.models.validation_result import (
    ValidationResult,
)
from app.repositories.in_memory_hitl_case_repository import (
    InMemoryHITLCaseRepository,
)


def create_case(
    case_id="HITL-001",
):
    return HITLCase(
        case_id=case_id,
        status=HITLCaseStatus.PENDING,
        validation_result=ValidationResult(
            status="EXCEPTION",
            exceptions=[],
        ),
        created_at=datetime.now(
            timezone.utc
        ),
        evidence=[
            {
                "field": "whole_row",
                "page_number": 1,
                "snip_path": (
                    "outputs/evidence/"
                    "row.png"
                ),
            }
        ],
    )


def test_save_and_get_case():

    repository = (
        InMemoryHITLCaseRepository()
    )

    case = create_case()

    saved_case = repository.save(
        case
    )

    assert saved_case is case

    retrieved_case = repository.get(
        "HITL-001"
    )

    assert retrieved_case is case

    assert (
        retrieved_case.case_id
        == "HITL-001"
    )

    assert (
        retrieved_case.status
        == HITLCaseStatus.PENDING
    )


def test_get_unknown_case_returns_none():

    repository = (
        InMemoryHITLCaseRepository()
    )

    result = repository.get(
        "HITL-DOES-NOT-EXIST"
    )

    assert result is None


def test_save_duplicate_case_is_rejected():

    repository = (
        InMemoryHITLCaseRepository()
    )

    case = create_case()

    repository.save(case)

    with pytest.raises(
        ValueError,
        match="HITL case already exists",
    ):
        repository.save(case)


def test_update_existing_case():

    repository = (
        InMemoryHITLCaseRepository()
    )

    case = create_case()

    repository.save(case)

    case.status = (
        HITLCaseStatus.REVIEWED
    )

    updated_case = repository.update(
        case
    )

    assert updated_case is case

    retrieved_case = repository.get(
        "HITL-001"
    )

    assert (
        retrieved_case.status
        == HITLCaseStatus.REVIEWED
    )


def test_update_preserves_evidence():

    repository = (
        InMemoryHITLCaseRepository()
    )

    case = create_case()

    original_evidence = (
        case.evidence
    )

    repository.save(case)

    case.status = (
        HITLCaseStatus.REVIEWED
    )

    repository.update(case)

    retrieved_case = repository.get(
        "HITL-001"
    )

    assert (
        retrieved_case.evidence
        == original_evidence
    )

    assert (
        retrieved_case.evidence[0][
            "field"
        ]
        == "whole_row"
    )


def test_update_unknown_case_is_rejected():

    repository = (
        InMemoryHITLCaseRepository()
    )

    case = create_case()

    with pytest.raises(
        ValueError,
        match="HITL case does not exist",
    ):
        repository.update(case)


def test_none_case_cannot_be_saved():

    repository = (
        InMemoryHITLCaseRepository()
    )

    with pytest.raises(
        ValueError,
        match="HITL case cannot be None",
    ):
        repository.save(None)


def test_none_case_cannot_be_updated():

    repository = (
        InMemoryHITLCaseRepository()
    )

    with pytest.raises(
        ValueError,
        match="HITL case cannot be None",
    ):
        repository.update(None)


def test_empty_case_id_is_rejected():

    repository = (
        InMemoryHITLCaseRepository()
    )

    with pytest.raises(
        ValueError,
        match="case_id cannot be empty",
    ):
        repository.get("")