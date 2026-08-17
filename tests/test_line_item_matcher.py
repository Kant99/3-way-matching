from app.matching.line_item_matcher import LineItemMatcher
from app.models.contract import Contract
from app.models.purchase_order import PurchaseOrder
from app.models.invoice import Invoice
from app.models.line_item import LineItem


def create_documents():
    contract = Contract(
        contract_id="CON-2026-001",
        contract_number="CON-2026-001",
        line_items=[
            LineItem(
                item_code="ITM-001",
                description="Industrial Safety Gloves",
                quantity=100,
                unit="Pair",
                unit_price=250.0,
            ),
            LineItem(
                item_code="ITM-002",
                description="Protective Safety Helmet",
                quantity=50,
                unit="Each",
                unit_price=800.0,
            ),
        ],
    )

    purchase_order = PurchaseOrder(
        po_id="PO-2026-1001",
        po_number="PO-2026-1001",
        contract_reference="CON-2026-001",
        line_items=[
            LineItem(
                item_code="ITM-001",
                description="Industrial Safety Gloves",
                quantity=100,
                unit="Pair",
                unit_price=250.0,
            ),
            LineItem(
                item_code="ITM-002",
                description="Protective Safety Helmet",
                quantity=50,
                unit="Each",
                unit_price=800.0,
            ),
        ],
    )

    invoice = Invoice(
        invoice_id="INV-2026-5001",
        invoice_number="INV-2026-5001",
        purchase_order_reference="PO-2026-1001",
        line_items=[
            LineItem(
                item_code="ITM-001",
                description="Industrial Safety Gloves",
                quantity=100,
                unit="Pair",
                unit_price=250.0,
            ),
            LineItem(
                item_code="ITM-002",
                description="Protective Safety Helmet",
                quantity=50,
                unit="Each",
                unit_price=800.0,
            ),
        ],
    )

    return contract, purchase_order, invoice


def test_line_items_match_by_item_code():
    contract, purchase_order, invoice = create_documents()

    matcher = LineItemMatcher()

    result = matcher.match(
        contract,
        purchase_order,
        invoice,
    )

    assert len(result["matches"]) == 2

    first = result["matches"][0]

    assert first["item_code"] == "ITM-001"
    assert first["contract"] is not None
    assert first["purchase_order"] is not None
    assert first["invoice"] is not None

    second = result["matches"][1]

    assert second["item_code"] == "ITM-002"
    assert second["contract"] is not None
    assert second["purchase_order"] is not None
    assert second["invoice"] is not None


def test_line_item_missing_from_invoice():
    contract, purchase_order, invoice = create_documents()

    invoice.line_items = [
        invoice.line_items[0]
    ]

    matcher = LineItemMatcher()

    result = matcher.match(
        contract,
        purchase_order,
        invoice,
    )

    assert len(result["matches"]) == 2

    itm_001 = result["matches"][0]
    itm_002 = result["matches"][1]

    assert itm_001["item_code"] == "ITM-001"
    assert itm_001["invoice"] is not None

    assert itm_002["item_code"] == "ITM-002"
    assert itm_002["invoice"] is None


def test_line_item_missing_from_purchase_order():
    contract, purchase_order, invoice = create_documents()

    purchase_order.line_items = [
        purchase_order.line_items[0]
    ]

    matcher = LineItemMatcher()

    result = matcher.match(
        contract,
        purchase_order,
        invoice,
    )

    assert len(result["matches"]) == 2

    itm_001 = result["matches"][0]
    itm_002 = result["matches"][1]

    assert itm_001["item_code"] == "ITM-001"
    assert itm_001["purchase_order"] is not None

    assert itm_002["item_code"] == "ITM-002"
    assert itm_002["purchase_order"] is None