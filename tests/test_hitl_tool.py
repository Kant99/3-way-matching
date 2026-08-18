from app.capabilities.matching_tools import route_to_hitl


def test_route_to_hitl_creates_pending_case():
    validation_result = {
        "status": "EXCEPTION",
        "exceptions": [
            {
                "type": "PRICE_MISMATCH",
                "item_code": "ITEM-001",
                "field": "unit_price",
                "expected": 250.0,
                "actual": 260.0,
                "tolerance": "±2%",
                "source": None,
                "evidence": [],
            }
        ],
    }

    result = route_to_hitl(validation_result)

    assert result["status"] == "HITL_REQUIRED"

    case = result["case"]

    assert case is not None
    assert case["case_id"].startswith("HITL-")
    assert case["status"] == "PENDING"
    assert case["reviewer"] is None

    validation = case["validation_result"]

    assert validation["status"] == "EXCEPTION"
    assert len(validation["exceptions"]) == 1

    exception = validation["exceptions"][0]

    assert exception["type"] == "PRICE_MISMATCH"
    assert exception["item_code"] == "ITEM-001"
    assert exception["field"] == "unit_price"
    assert exception["expected"] == 250.0
    assert exception["actual"] == 260.0
    assert exception["tolerance"] == "±2%"


def test_route_to_hitl_does_not_route_pass():
    validation_result = {
        "status": "PASS",
        "exceptions": [],
    }

    result = route_to_hitl(validation_result)

    assert result["status"] == "NO_HITL_REQUIRED"
    assert result["case"] is None


def test_route_to_hitl_preserves_evidence():
    validation_result = {
        "status": "EXCEPTION",
        "exceptions": [
            {
                "type": "PRICE_MISMATCH",
                "item_code": "ITEM-001",
                "field": "unit_price",
                "expected": 250.0,
                "actual": 260.0,
                "tolerance": "±2%",
                "source": {
                    "document_id": "INV-2026-5001",
                    "document_path": "data/invoices/invoice.pdf",
                    "page_number": 1,
                    "polygon": [
                        [10, 10],
                        [100, 10],
                        [100, 50],
                        [10, 50],
                    ],
                },
                "evidence": [
                    {
                        "document_id": "INV-2026-5001",
                        "page_number": 1,
                    }
                ],
            }
        ],
    }

    result = route_to_hitl(validation_result)

    assert result["status"] == "HITL_REQUIRED"

    exception = (
        result["case"]["validation_result"]["exceptions"][0]
    )

    assert exception["source"]["document_id"] == "INV-2026-5001"
    assert exception["source"]["page_number"] == 1

    assert exception["evidence"] == [
        {
            "document_id": "INV-2026-5001",
            "page_number": 1,
        }
    ]