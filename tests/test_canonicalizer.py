from app.canonicalization.canonicalizer import Canonicalizer
from app.models.contract import Contract
from app.models.invoice import Invoice
from app.models.line_item import LineItem
from app.models.purchase_order import PurchaseOrder
from app.models.source_reference import SourceReference
from app.canonicalization.canonicalizer import Canonicalizer
def test_canonicalize_purchase_order():

    extracted = {
        "document_path": (
            "data/purchase_orders/"
            "purchase_order_PO-2026-1001.pdf"
        ),

        "po_number": {
            "value": "PO-2026-1001",
            "source": [
                {
                    "page_number": 1,
                    "polygon": [
                        {"x": 0.8, "y": 1.2},
                        {"x": 3.0, "y": 1.2},
                        {"x": 3.0, "y": 1.5},
                        {"x": 0.8, "y": 1.5},
                    ],
                }
            ],
        },

        "po_date": {
            "value": "05 August 2026",
            "source": [],
        },

        "contract_reference": {
            "value": "CON-2026-001",
            "source": [],
        },

        "buyer": {
            "value": "ABC Manufacturing Pvt. Ltd.",
            "source": [],
        },

        "supplier": {
            "value": "Global Office Supplies Ltd.",
            "source": [],
        },

        "line_items": [
            {
                "item_code": {
                    "value": "ITM-001",
                    "source": [],
                },
                "description": {
                    "value": "Industrial Safety Gloves",
                    "source": [],
                },
                "quantity": {
                    "value": "100",
                    "source": [],
                },
                "unit": {
                    "value": "Pair",
                    "source": [],
                },
                "unit_price": {
                    "value": "250.00",
                    "source": [],
                },
                "amount": {
                    "value": "25,000.00",
                    "source": [],
                },
            },
            {
                "item_code": {
                    "value": "ITM-002",
                    "source": [],
                },
                "description": {
                    "value": "Protective Safety Helmet",
                    "source": [],
                },
                "quantity": {
                    "value": "50",
                    "source": [],
                },
                "unit": {
                    "value": "Each",
                    "source": [],
                },
                "unit_price": {
                    "value": "800.00",
                    "source": [],
                },
                "amount": {
                    "value": "40,000.00",
                    "source": [],
                },
            },
        ],
    }

    canonicalizer = Canonicalizer()

    po = canonicalizer.canonicalize_purchase_order(
        extracted,
        "PO-DOC-001",
    )

    assert isinstance(po, PurchaseOrder)

    assert po.po_id == "PO-DOC-001"
    assert po.po_number == "PO-2026-1001"
    assert po.contract_reference == "CON-2026-001"
    assert po.po_date == "05 August 2026"
    assert po.buyer == "ABC Manufacturing Pvt. Ltd."
    assert po.supplier == "Global Office Supplies Ltd."

    assert len(po.line_items) == 2

    first_item = po.line_items[0]

    assert first_item.item_code == "ITM-001"
    assert first_item.description == (
        "Industrial Safety Gloves"
    )
    assert first_item.quantity == 100.0
    assert first_item.unit == "Pair"
    assert first_item.unit_price == 250.0
    assert first_item.amount == 25000.0

    second_item = po.line_items[1]

    assert second_item.item_code == "ITM-002"
    assert second_item.quantity == 50.0
    assert second_item.unit_price == 800.0
    assert second_item.amount == 40000.0