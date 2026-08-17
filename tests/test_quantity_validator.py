from app.matching.quantity_validator import QuantityValidator
from app.models.contract import Contract
from app.models.purchase_order import PurchaseOrder
from app.models.invoice import Invoice
from app.models.line_item import LineItem


def create_documents(
    po_quantity=100,
    invoice_quantity=100,
):
    contract = Contract(
        contract_id="CON-2026-001",
        contract_number="CON-2026-001",
        quantity_tolerance="+5%",
        line_items=[
            LineItem(
                item_code="ITM-001",
                description="Industrial Safety Gloves",
                quantity=100,
                unit="Pair",
                unit_price=250.0,
            )
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
                quantity=po_quantity,
                unit="Pair",
                unit_price=250.0,
            )
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
                quantity=invoice_quantity,
                unit="Pair",
                unit_price=250.0,
            )
        ],
    )

    return contract, purchase_order, invoice


def get_match(contract, purchase_order, invoice):
    return [
        {
            "item_code": "ITM-001",
            "contract": contract.line_items[0],
            "purchase_order": purchase_order.line_items[0],
            "invoice": invoice.line_items[0],
        }
    ]


def test_quantity_validation_passes_for_normal_quantity():
    contract, purchase_order, invoice = create_documents(
        po_quantity=100,
        invoice_quantity=100,
    )

    validator = QuantityValidator()

    result = validator.validate(
        contract,
        purchase_order,
        invoice,
        get_match(contract, purchase_order, invoice),
    )

    assert result.status == "PASS"
    assert result.exceptions == []


def test_po_quantity_passes_at_contract_tolerance_limit():
    contract, purchase_order, invoice = create_documents(
        po_quantity=105,
        invoice_quantity=105,
    )

    validator = QuantityValidator()

    result = validator.validate(
        contract,
        purchase_order,
        invoice,
        get_match(contract, purchase_order, invoice),
    )

    assert result.status == "PASS"
    assert result.exceptions == []


def test_po_quantity_fails_above_contract_tolerance():
    contract, purchase_order, invoice = create_documents(
        po_quantity=106,
        invoice_quantity=106,
    )

    validator = QuantityValidator()

    result = validator.validate(
        contract,
        purchase_order,
        invoice,
        get_match(contract, purchase_order, invoice),
    )

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 1

    exception = result.exceptions[0]

    assert exception.type == "QUANTITY_MISMATCH"
    assert exception.item_code == "ITM-001"
    assert exception.expected == 105
    assert exception.actual == 106
    assert exception.tolerance == "+5%"


def test_invoice_quantity_passes_when_not_greater_than_po():
    contract, purchase_order, invoice = create_documents(
        po_quantity=100,
        invoice_quantity=98,
    )

    validator = QuantityValidator()

    result = validator.validate(
        contract,
        purchase_order,
        invoice,
        get_match(contract, purchase_order, invoice),
    )

    assert result.status == "PASS"
    assert result.exceptions == []


def test_invoice_quantity_fails_when_greater_than_po():
    contract, purchase_order, invoice = create_documents(
        po_quantity=100,
        invoice_quantity=101,
    )

    validator = QuantityValidator()

    result = validator.validate(
        contract,
        purchase_order,
        invoice,
        get_match(contract, purchase_order, invoice),
    )

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 1

    exception = result.exceptions[0]

    assert exception.type == "QUANTITY_MISMATCH"
    assert exception.item_code == "ITM-001"
    assert exception.expected == 100
    assert exception.actual == 101
    assert exception.tolerance is None