from pathlib import Path

from app.capabilities.hitl_evidence import (
    HITLEvidenceService,
)


INVOICE_PATH = (
    "data/invoices/invoice_INV-2026-5001.pdf"
)


def test_hitl_evidence_generates_whole_row():
    invoice_path = Path(
        INVOICE_PATH
    )

    assert invoice_path.exists()

    line_item = {
        "item_code": {
            "value": "ITM-001",
            "source": [
                {
                    "page_number": 1,
                    "polygon": [
                        {"x": 1.316, "y": 3.6148},
                        {"x": 1.7064, "y": 3.6148},
                        {"x": 1.7064, "y": 3.7241},
                        {"x": 1.3161, "y": 3.7237},
                    ],
                }
            ],
        },
        "description": {
            "value": "Industrial Safety Gloves",
            "source": [
                {
                    "page_number": 1,
                    "polygon": [
                        {"x": 2.1822, "y": 3.6134},
                        {"x": 3.2931, "y": 3.6139},
                        {"x": 3.293, "y": 3.7336},
                        {"x": 2.1821, "y": 3.733},
                    ],
                }
            ],
        },
        "quantity": {
            "value": 100,
            "source": [
                {
                    "page_number": 1,
                    "polygon": [
                        {"x": 3.9589, "y": 3.6201},
                        {"x": 4.1377, "y": 3.6195},
                        {"x": 4.1377, "y": 3.7199},
                        {"x": 3.9588, "y": 3.7201},
                    ],
                }
            ],
        },
        "unit_price": {
            "value": 250.00,
            "source": [
                {
                    "page_number": 1,
                    "polygon": [
                        {"x": 5.1295, "y": 3.6172},
                        {"x": 5.4651, "y": 3.6166},
                        {"x": 5.4648, "y": 3.7228},
                        {"x": 5.1297, "y": 3.7238},
                    ],
                }
            ],
        },
        "amount": {
            "value": 25000.00,
            "source": [
                {
                    "page_number": 1,
                    "polygon": [
                        {"x": 6.3083, "y": 3.615},
                        {"x": 6.7915, "y": 3.615},
                        {"x": 6.7915, "y": 3.7263},
                        {"x": 6.3084, "y": 3.7282},
                    ],
                }
            ],
        },
    }

    service = HITLEvidenceService(
        output_dir="outputs/evidence"
    )

    result = service.generate_row_evidence(
        document_path=str(invoice_path),
        line_item=line_item,
        item_code="ITM-001",
    )

    assert result["field"] == "whole_row"
    assert result["page_number"] == 1
    assert result["polygon"]

    output_path = Path(
        result["snip_path"]
    )

    assert output_path.exists()
    assert output_path.is_file()

    print()
    print(
        f"HITL evidence generated: "
        f"{output_path}"
    )