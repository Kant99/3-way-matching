from app.matching.relationship_validator import RelationshipValidator
from app.models.contract import Contract
from app.models.purchase_order import PurchaseOrder
from app.models.invoice import Invoice


def create_valid_documents():
    contract = Contract(
        contract_id="CON-2026-001",
        contract_number="CON-2026-001",
    )

    purchase_order = PurchaseOrder(
        po_id="PO-2026-1001",
        po_number="PO-2026-1001",
        contract_reference="CON-2026-001",
    )

    invoice = Invoice(
        invoice_id="INV-2026-5001",
        invoice_number="INV-2026-5001",
        purchase_order_reference="PO-2026-1001",
    )

    return contract, purchase_order, invoice


# ============================================================
# POSITIVE TESTS
# ============================================================

def test_relationship_validation_passes():
    contract, purchase_order, invoice = create_valid_documents()

    result = RelationshipValidator().validate(
        contract,
        purchase_order,
        invoice,
    )

    assert result.status == "PASS"
    assert result.exceptions == []


# ============================================================
# NEGATIVE TESTS
# ============================================================

def test_relationship_validation_fails_when_po_references_wrong_contract():
    contract, purchase_order, invoice = create_valid_documents()

    purchase_order.contract_reference = "CON-2026-999"

    result = RelationshipValidator().validate(
        contract,
        purchase_order,
        invoice,
    )

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 1

    exception = result.exceptions[0]

    assert exception.type == "CONTRACT_REFERENCE_MISMATCH"
    assert exception.expected == "CON-2026-001"
    assert exception.actual == "CON-2026-999"


def test_relationship_validation_fails_when_invoice_references_wrong_po():
    contract, purchase_order, invoice = create_valid_documents()

    invoice.purchase_order_reference = "PO-2026-9999"

    result = RelationshipValidator().validate(
        contract,
        purchase_order,
        invoice,
    )

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 1

    exception = result.exceptions[0]

    assert exception.type == "PO_REFERENCE_MISMATCH"
    assert exception.expected == "PO-2026-1001"
    assert exception.actual == "PO-2026-9999"


def test_relationship_validation_returns_two_exceptions_for_two_invalid_references():
    contract, purchase_order, invoice = create_valid_documents()

    purchase_order.contract_reference = "CON-2026-999"
    invoice.purchase_order_reference = "PO-2026-9999"

    result = RelationshipValidator().validate(
        contract,
        purchase_order,
        invoice,
    )

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 2

    first_exception = result.exceptions[0]
    second_exception = result.exceptions[1]

    assert first_exception.type == "CONTRACT_REFERENCE_MISMATCH"
    assert first_exception.expected == "CON-2026-001"
    assert first_exception.actual == "CON-2026-999"

    assert second_exception.type == "PO_REFERENCE_MISMATCH"
    assert second_exception.expected == "PO-2026-1001"
    assert second_exception.actual == "PO-2026-9999"