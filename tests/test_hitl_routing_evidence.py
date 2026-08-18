from datetime import datetime, timezone

from app.capabilities.hitl_routing import (
    HITLRoutingCapability,
)
from app.models.validation_result import (
    ValidationException,
    ValidationResult,
)


def test_hitl_routing_transfers_whole_row_evidence():

    evidence = {
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

    exception = ValidationException(
        type="PRICE_MISMATCH",
        item_code="ITM-001",
        field="unit_price",
        expected=250,
        actual=260,
        tolerance="±2%",
        evidence=[
            evidence
        ],
    )

    validation_result = ValidationResult(
        status="EXCEPTION",
        exceptions=[
            exception
        ],
    )

    router = HITLRoutingCapability()

    hitl_case = router.route(
        validation_result
    )

    assert hitl_case is not None

    assert hitl_case.evidence

    assert len(
        hitl_case.evidence
    ) == 1

    assert (
        hitl_case.evidence[0]
        == evidence
    )

    assert (
        hitl_case.evidence[0]["field"]
        == "whole_row"
    )

    assert (
        hitl_case.evidence[0]["page_number"]
        == 1
    )