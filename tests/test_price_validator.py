import pytest

from app.matching.price_validator import PriceValidator
from app.models.contract import Contract
from app.models.purchase_order import PurchaseOrder
from app.models.invoice import Invoice
from app.models.line_item import LineItem


def create_documents(
    po_price=250.0,
    invoice_price=250.0,
):
    contract = Contract(
        contract_id="CON-2026-001",
        contract_number="CON-2026-001",
        price_tolerance="±2%",
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
                quantity=100,
                unit="Pair",
                unit_price=po_price,
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
                quantity=100,
                unit="Pair",
                unit_price=invoice_price,
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


# ============================================================
# POSITIVE TESTS
# ============================================================

def test_price_validation_passes_for_normal_price():
    contract, purchase_order, invoice = create_documents(
        po_price=250.0,
        invoice_price=250.0,
    )

    result = PriceValidator().validate(
        contract,
        purchase_order,
        invoice,
        get_match(contract, purchase_order, invoice),
    )

    assert result.status == "PASS"
    assert result.exceptions == []


def test_po_price_passes_at_lower_tolerance_boundary():
    # 250 - 2% = 245
    contract, purchase_order, invoice = create_documents(
        po_price=245.0,
        invoice_price=245.0,
    )

    result = PriceValidator().validate(
        contract,
        purchase_order,
        invoice,
        get_match(contract, purchase_order, invoice),
    )

    assert result.status == "PASS"
    assert result.exceptions == []


def test_po_price_passes_at_upper_tolerance_boundary():
    # 250 + 2% = 255
    contract, purchase_order, invoice = create_documents(
        po_price=255.0,
        invoice_price=255.0,
    )

    result = PriceValidator().validate(
        contract,
        purchase_order,
        invoice,
        get_match(contract, purchase_order, invoice),
    )

    assert result.status == "PASS"
    assert result.exceptions == []


def test_invoice_price_passes_when_less_than_po_price():
    contract, purchase_order, invoice = create_documents(
        po_price=250.0,
        invoice_price=249.0,
    )

    result = PriceValidator().validate(
        contract,
        purchase_order,
        invoice,
        get_match(contract, purchase_order, invoice),
    )

    assert result.status == "PASS"
    assert result.exceptions == []


def test_invoice_price_passes_when_equal_to_po_price():
    contract, purchase_order, invoice = create_documents(
        po_price=250.0,
        invoice_price=250.0,
    )

    result = PriceValidator().validate(
        contract,
        purchase_order,
        invoice,
        get_match(contract, purchase_order, invoice),
    )

    assert result.status == "PASS"
    assert result.exceptions == []


# ============================================================
# NEGATIVE TESTS
# ============================================================

def test_po_price_fails_below_lower_tolerance():
    # 250 - 2% = 245
    # 244 is below allowed minimum
    contract, purchase_order, invoice = create_documents(
        po_price=244.0,
        invoice_price=244.0,
    )

    result = PriceValidator().validate(
        contract,
        purchase_order,
        invoice,
        get_match(contract, purchase_order, invoice),
    )

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 1

    exception = result.exceptions[0]

    assert exception.type == "PRICE_MISMATCH"
    assert exception.item_code == "ITM-001"
    assert exception.expected["min"] == 245.0
    assert exception.expected["max"] == 255.0
    assert exception.actual == 244.0
    assert exception.tolerance == "±2%"


def test_po_price_fails_above_upper_tolerance():
    # 250 + 2% = 255
    # 256 is above allowed maximum
    contract, purchase_order, invoice = create_documents(
        po_price=256.0,
        invoice_price=256.0,
    )

    result = PriceValidator().validate(
        contract,
        purchase_order,
        invoice,
        get_match(contract, purchase_order, invoice),
    )

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 1

    exception = result.exceptions[0]

    assert exception.type == "PRICE_MISMATCH"
    assert exception.item_code == "ITM-001"
    assert exception.expected["min"] == 245.0
    assert exception.expected["max"] == 255.0
    assert exception.actual == 256.0
    assert exception.tolerance == "±2%"


def test_invoice_price_fails_when_greater_than_po():
    contract, purchase_order, invoice = create_documents(
        po_price=250.0,
        invoice_price=251.0,
    )

    result = PriceValidator().validate(
        contract,
        purchase_order,
        invoice,
        get_match(contract, purchase_order, invoice),
    )

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 1

    exception = result.exceptions[0]

    assert exception.type == "PRICE_MISMATCH"
    assert exception.item_code == "ITM-001"
    assert exception.expected == 250.0
    assert exception.actual == 251.0
    assert exception.tolerance is None


def test_po_price_fails_and_invoice_price_is_also_above_po():
    """
    Two independent violations:

    Contract price = 250
    Allowed range = 245 to 255

    PO price = 256
    → Contract → PO violation

    Invoice price = 257
    → PO → Invoice violation
    """

    contract, purchase_order, invoice = create_documents(
        po_price=256.0,
        invoice_price=257.0,
    )

    result = PriceValidator().validate(
        contract,
        purchase_order,
        invoice,
        get_match(contract, purchase_order, invoice),
    )

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 2

    first_exception = result.exceptions[0]
    second_exception = result.exceptions[1]

    assert first_exception.type == "PRICE_MISMATCH"
    assert first_exception.item_code == "ITM-001"
    assert first_exception.expected["min"] == 245.0
    assert first_exception.expected["max"] == 255.0
    assert first_exception.actual == 256.0

    assert second_exception.type == "PRICE_MISMATCH"
    assert second_exception.item_code == "ITM-001"
    assert second_exception.expected == 256.0
    assert second_exception.actual == 257.0
    assert second_exception.tolerance is None