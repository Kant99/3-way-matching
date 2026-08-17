from app.models.validation_result import (
    ValidationException,
    ValidationResult,
)
from app.models.source_reference import SourceReference


def test_validation_exception_preserves_source_reference():
    source = SourceReference(
        document_id="INV-2026-5001",
        document_path="data/invoices/invoice_INV-2026-5001.pdf",
        page_number=1,
        polygon=[
            {"x": 1.0, "y": 2.0},
            {"x": 2.0, "y": 2.0},
            {"x": 2.0, "y": 3.0},
            {"x": 1.0, "y": 3.0},
        ],
    )

    exception = ValidationException(
        type="QUANTITY_MISMATCH",
        item_code="ITM-001",
        expected=105,
        actual=108,
        tolerance="+5%",
        source=source,
    )

    assert exception.type == "QUANTITY_MISMATCH"
    assert exception.item_code == "ITM-001"
    assert exception.expected == 105
    assert exception.actual == 108
    assert exception.tolerance == "+5%"
    assert exception.source == source


def test_validation_result_defaults_to_empty_exceptions():
    result = ValidationResult(
        status="PASS"
    )

    assert result.status == "PASS"
    assert result.exceptions == []


def test_validation_result_can_contain_exceptions():
    exception = ValidationException(
        type="PRICE_MISMATCH",
        item_code="ITM-001",
        expected=255.0,
        actual=260.0,
        tolerance="±2%",
    )

    result = ValidationResult(
        status="EXCEPTION",
        exceptions=[exception],
    )

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 1
    assert result.exceptions[0].type == "PRICE_MISMATCH"
    assert result.exceptions[0].actual == 260.0