from pathlib import Path

from app.capabilities.evidence_generator import EvidenceGenerator


CONTRACT_PATH = (
    "data/contracts/contract_CON-2026-001.pdf"
)


def test_evidence_generation():

    generator = EvidenceGenerator(
        output_dir="outputs/evidence"
    )

    result = generator.generate_evidence(
        exception_type="QUANTITY_MISMATCH",
        evidence_references=[
            {
                "document_path": CONTRACT_PATH,
                "field": "quantity",
                "page_number": 1,
                "polygon": [
                    {
                        "x": 3.7254,
                        "y": 3.7496,
                    },
                    {
                        "x": 4.6725,
                        "y": 3.7496,
                    },
                    {
                        "x": 4.6725,
                        "y": 3.9993,
                    },
                    {
                        "x": 3.7316,
                        "y": 3.9993,
                    },
                ],
            }
        ],
    )

    assert result["exception_type"] == (
        "QUANTITY_MISMATCH"
    )

    assert len(result["evidence"]) == 1

    snip_path = Path(
        result["evidence"][0]["snip_path"]
    )

    assert snip_path.exists()
    assert snip_path.stat().st_size > 0


def test_evidence_generation_multiple_documents():

    generator = EvidenceGenerator(
        output_dir="outputs/evidence"
    )

    result = generator.generate_evidence(
        exception_type="PRICE_MISMATCH",
        evidence_references=[
            {
                "document_path": CONTRACT_PATH,
                "field": "unit_price",
                "page_number": 1,
                "polygon": [
                    {
                        "x": 5.3517,
                        "y": 3.7496,
                    },
                    {
                        "x": 6.492,
                        "y": 3.7496,
                    },
                    {
                        "x": 6.492,
                        "y": 3.9993,
                    },
                    {
                        "x": 5.3517,
                        "y": 3.9993,
                    },
                ],
            },
            {
                "document_path": CONTRACT_PATH,
                "field": "tax",
                "page_number": 1,
                "polygon": [
                    {
                        "x": 6.492,
                        "y": 3.7496,
                    },
                    {
                        "x": 7.1151,
                        "y": 3.7496,
                    },
                    {
                        "x": 7.1151,
                        "y": 3.9993,
                    },
                    {
                        "x": 6.492,
                        "y": 3.9993,
                    },
                ],
            },
        ],
    )

    assert result["exception_type"] == (
        "PRICE_MISMATCH"
    )

    assert len(result["evidence"]) == 2

    for evidence in result["evidence"]:
        assert Path(
            evidence["snip_path"]
        ).exists()


def test_evidence_generation_invalid_reference():

    generator = EvidenceGenerator()

    try:
        generator.generate_evidence(
            exception_type="QUANTITY_MISMATCH",
            evidence_references=[
                {
                    "document_path": CONTRACT_PATH,
                    "field": "quantity",
                }
            ],
        )

        assert False, "Expected ValueError"

    except ValueError as exc:
        assert "page_number" in str(exc)