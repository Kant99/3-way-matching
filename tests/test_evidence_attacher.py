from unittest.mock import Mock

from app.matching.evidence_attacher import EvidenceAttacher
from app.models.source_reference import SourceReference
from app.models.validation_result import ValidationException


def create_source():
    return SourceReference(
        document_id="INV-2026-5001",
        document_path=(
            "data/invoices/"
            "invoice_INV-2026-5001.pdf"
        ),
        page_number=1,
        polygon=[
            {"x": 1.0, "y": 2.0},
            {"x": 2.0, "y": 2.0},
            {"x": 2.0, "y": 3.0},
            {"x": 1.0, "y": 3.0},
        ],
    )


def test_evidence_attacher_attaches_generated_evidence():
    evidence_generator = Mock()

    evidence_generator.generate_evidence.return_value = {
        "exception_type": "QUANTITY_MISMATCH",
        "evidence": [
            {
                "document_path": (
                    "data/invoices/"
                    "invoice_INV-2026-5001.pdf"
                ),
                "field": "quantity",
                "page_number": 1,
                "snip_path": (
                    "outputs/evidence/"
                    "invoice_INV-2026-5001_quantity_0.png"
                ),
            }
        ],
    }

    exception = ValidationException(
        type="QUANTITY_MISMATCH",
        item_code="ITM-001",
        field="quantity",
        expected=105.0,
        actual=108,
        tolerance="+5%",
        source=create_source(),
    )

    attacher = EvidenceAttacher(
        evidence_generator=evidence_generator
    )

    result = attacher.attach(exception)

    assert result is exception
    assert len(result.evidence) == 1

    assert (
        result.evidence[0]["field"]
        == "quantity"
    )

    assert (
        result.evidence[0]["snip_path"]
        == (
            "outputs/evidence/"
            "invoice_INV-2026-5001_quantity_0.png"
        )
    )

    evidence_generator.generate_evidence.assert_called_once_with(
        exception_type="QUANTITY_MISMATCH",
        evidence_references=[
            {
                "document_path": (
                    "data/invoices/"
                    "invoice_INV-2026-5001.pdf"
                ),
                "field": "quantity",
                "page_number": 1,
                "polygon": [
                    {"x": 1.0, "y": 2.0},
                    {"x": 2.0, "y": 2.0},
                    {"x": 2.0, "y": 3.0},
                    {"x": 1.0, "y": 3.0},
                ],
            }
        ],
    )


def test_evidence_attacher_does_nothing_without_source():
    evidence_generator = Mock()

    exception = ValidationException(
        type="QUANTITY_MISMATCH",
        item_code="ITM-001",
        field="quantity",
        expected=105.0,
        actual=108,
        tolerance="+5%",
        source=None,
    )

    attacher = EvidenceAttacher(
        evidence_generator=evidence_generator
    )

    result = attacher.attach(exception)

    assert result is exception
    assert result.evidence == []

    evidence_generator.generate_evidence.assert_not_called()


def test_evidence_attacher_does_nothing_without_field():
    evidence_generator = Mock()

    exception = ValidationException(
        type="QUANTITY_MISMATCH",
        item_code="ITM-001",
        field=None,
        expected=105.0,
        actual=108,
        tolerance="+5%",
        source=create_source(),
    )

    attacher = EvidenceAttacher(
        evidence_generator=evidence_generator
    )

    result = attacher.attach(exception)

    assert result is exception
    assert result.evidence == []

    evidence_generator.generate_evidence.assert_not_called()