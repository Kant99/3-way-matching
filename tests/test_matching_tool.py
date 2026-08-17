from app.capabilities.matching_tools import run_3_way_matching


def test_run_3_way_matching_valid_case():
    contract = {
        "contract_id": "C001",
        "contract_number": "CON-001",
        "quantity_tolerance": "+5%",
        "price_tolerance": "±2%",
        "line_items": [
            {
                "item_code": "ITEM-001",
                "description": "Test Item",
                "quantity": 100,
                "unit": "EA",
                "unit_price": 250,
                "amount": 25000,
            }
        ],
    }

    purchase_order = {
        "po_id": "PO001",
        "po_number": "PO-001",
        "contract_reference": "CON-001",
        "line_items": [
            {
                "item_code": "ITEM-001",
                "description": "Test Item",
                "quantity": 100,
                "unit": "EA",
                "unit_price": 250,
                "amount": 25000,
            }
        ],
    }

    invoice = {
        "invoice_id": "INV001",
        "invoice_number": "INV-001",
        "purchase_order_reference": "PO-001",
        "line_items": [
            {
                "item_code": "ITEM-001",
                "description": "Test Item",
                "quantity": 100,
                "unit": "EA",
                "unit_price": 250,
                "amount": 25000,
            }
        ],
    }

    result = run_3_way_matching(
        contract=contract,
        purchase_order=purchase_order,
        invoice=invoice,
    )

    assert result["status"] == "PASS"
    assert result["exceptions"] == []

def test_run_3_way_matching_exception_case():
    contract = {
        "contract_id": "C001",
        "contract_number": "CON-001",
        "quantity_tolerance": "+5%",
        "price_tolerance": "±2%",
        "line_items": [
            {
                "item_code": "ITEM-001",
                "description": "Test Item",
                "quantity": 100,
                "unit": "EA",
                "unit_price": 250,
                "amount": 25000,
            }
        ],
    }

    purchase_order = {
        "po_id": "PO001",
        "po_number": "PO-001",
        "contract_reference": "CON-001",
        "line_items": [
            {
                "item_code": "ITEM-001",
                "description": "Test Item",
                "quantity": 106,
                "unit": "EA",
                "unit_price": 256,
                "amount": 27136,
            }
        ],
    }

    invoice = {
        "invoice_id": "INV001",
        "invoice_number": "INV-001",
        "purchase_order_reference": "PO-001",
        "line_items": [
            {
                "item_code": "ITEM-001",
                "description": "Test Item",
                "quantity": 107,
                "unit": "EA",
                "unit_price": 257,
                "amount": 27499,
            }
        ],
    }

    result = run_3_way_matching(
        contract=contract,
        purchase_order=purchase_order,
        invoice=invoice,
    )

    assert result["status"] == "EXCEPTION"

    exception_types = [
        exception["type"]
        for exception in result["exceptions"]
    ]

    assert exception_types.count("QUANTITY_MISMATCH") == 2
    assert exception_types.count("PRICE_MISMATCH") == 2
    assert len(result["exceptions"]) == 4