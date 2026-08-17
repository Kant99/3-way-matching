from app.matching.matching_engine import MatchingEngine
from app.models.contract import Contract
from app.models.purchase_order import PurchaseOrder
from app.models.invoice import Invoice
from app.models.line_item import LineItem


def create_documents(
    po_quantity=100,
    invoice_quantity=100,
    po_price=250.0,
    invoice_price=250.0,
    contract_reference="CON-2026-001",
    invoice_po_reference="PO-2026-1001",
):
    contract = Contract(
        contract_id="CON-2026-001",
        contract_number="CON-2026-001",
        quantity_tolerance="+5%",
        price_tolerance="±2%",
        line_items=[
            LineItem(
                item_code="ITM-001",
                description="Industrial Safety Gloves",
                quantity=100,
                unit="Pair",
                unit_price=250.0,
            ),
        ],
    )

    purchase_order = PurchaseOrder(
        po_id="PO-2026-1001",
        po_number="PO-2026-1001",
        contract_reference=contract_reference,
        line_items=[
            LineItem(
                item_code="ITM-001",
                description="Industrial Safety Gloves",
                quantity=po_quantity,
                unit="Pair",
                unit_price=po_price,
            ),
        ],
    )

    invoice = Invoice(
        invoice_id="INV-2026-5001",
        invoice_number="INV-2026-5001",
        purchase_order_reference=invoice_po_reference,
        line_items=[
            LineItem(
                item_code="ITM-001",
                description="Industrial Safety Gloves",
                quantity=invoice_quantity,
                unit="Pair",
                unit_price=invoice_price,
            ),
        ],
    )

    return contract, purchase_order, invoice


# ============================================================
# POSITIVE VALIDATION
# ============================================================

def test_full_validation_passes_for_valid_three_way_match():
    contract, purchase_order, invoice = create_documents()

    result = MatchingEngine().match(
        contract,
        purchase_order,
        invoice,
    )

    assert result.status == "PASS"
    assert result.exceptions == []


# ============================================================
# POSITIVE — QUANTITY BOUNDARY
# ============================================================

def test_full_validation_passes_at_quantity_tolerance_boundary():
    """
    Contract quantity = 100
    Contract tolerance = +5%
    Maximum allowed PO quantity = 105

    PO = 105
    Invoice = 105

    Expected: PASS
    """

    contract, purchase_order, invoice = create_documents(
        po_quantity=105,
        invoice_quantity=105,
    )

    result = MatchingEngine().match(
        contract,
        purchase_order,
        invoice,
    )

    assert result.status == "PASS"
    assert result.exceptions == []


# ============================================================
# POSITIVE — PRICE BOUNDARIES
# ============================================================

def test_full_validation_passes_at_lower_price_boundary():
    """
    Contract price = 250
    Tolerance = ±2%
    Minimum allowed = 245
    """

    contract, purchase_order, invoice = create_documents(
        po_price=245.0,
        invoice_price=245.0,
    )

    result = MatchingEngine().match(
        contract,
        purchase_order,
        invoice,
    )

    assert result.status == "PASS"
    assert result.exceptions == []


def test_full_validation_passes_at_upper_price_boundary():
    """
    Contract price = 250
    Tolerance = ±2%
    Maximum allowed = 255
    """

    contract, purchase_order, invoice = create_documents(
        po_price=255.0,
        invoice_price=255.0,
    )

    result = MatchingEngine().match(
        contract,
        purchase_order,
        invoice,
    )

    assert result.status == "PASS"
    assert result.exceptions == []


# ============================================================
# NEGATIVE — CONTRACT / PO RELATIONSHIP
# ============================================================

def test_full_validation_detects_wrong_contract_reference():
    contract, purchase_order, invoice = create_documents(
        contract_reference="CON-2026-999",
    )

    result = MatchingEngine().match(
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


# ============================================================
# NEGATIVE — INVOICE / PO RELATIONSHIP
# ============================================================

def test_full_validation_detects_wrong_po_reference():
    contract, purchase_order, invoice = create_documents(
        invoice_po_reference="PO-2026-9999",
    )

    result = MatchingEngine().match(
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


# ============================================================
# NEGATIVE — PO QUANTITY ABOVE CONTRACT TOLERANCE
# ============================================================

def test_full_validation_detects_po_quantity_above_tolerance():
    """
    Contract = 100
    Tolerance = +5%
    Allowed = 105

    PO = 106
    Invoice = 106

    Only Contract → PO should fail.
    """

    contract, purchase_order, invoice = create_documents(
        po_quantity=106,
        invoice_quantity=106,
    )

    result = MatchingEngine().match(
        contract,
        purchase_order,
        invoice,
    )

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 1

    exception = result.exceptions[0]

    assert exception.type == "QUANTITY_MISMATCH"
    assert exception.item_code == "ITM-001"
    assert exception.field == "quantity"
    assert exception.expected == 105.0
    assert exception.actual == 106
    assert exception.tolerance == "+5%"


# ============================================================
# NEGATIVE — INVOICE QUANTITY ABOVE PO
# ============================================================

def test_full_validation_detects_invoice_quantity_above_po():
    """
    PO = 100
    Invoice = 101

    Expected:
    PO → Invoice quantity exception.
    """

    contract, purchase_order, invoice = create_documents(
        po_quantity=100,
        invoice_quantity=101,
    )

    result = MatchingEngine().match(
        contract,
        purchase_order,
        invoice,
    )

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 1

    exception = result.exceptions[0]

    assert exception.type == "QUANTITY_MISMATCH"
    assert exception.item_code == "ITM-001"
    assert exception.field == "quantity"
    assert exception.expected == 100
    assert exception.actual == 101
    assert exception.tolerance is None


# ============================================================
# NEGATIVE — PO PRICE BELOW CONTRACT TOLERANCE
# ============================================================

def test_full_validation_detects_po_price_below_tolerance():
    """
    Contract = 250
    Allowed range = 245–255

    PO = 244

    Expected:
    Contract → PO price exception.
    """

    contract, purchase_order, invoice = create_documents(
        po_price=244.0,
        invoice_price=244.0,
    )

    result = MatchingEngine().match(
        contract,
        purchase_order,
        invoice,
    )

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 1

    exception = result.exceptions[0]

    assert exception.type == "PRICE_MISMATCH"
    assert exception.item_code == "ITM-001"
    assert exception.field == "unit_price"
    assert exception.expected["min"] == 245.0
    assert exception.expected["max"] == 255.0
    assert exception.actual == 244.0
    assert exception.tolerance == "±2%"


# ============================================================
# NEGATIVE — PO PRICE ABOVE CONTRACT TOLERANCE
# ============================================================

def test_full_validation_detects_po_price_above_tolerance():
    """
    Contract = 250
    Allowed range = 245–255

    PO = 256
    """

    contract, purchase_order, invoice = create_documents(
        po_price=256.0,
        invoice_price=256.0,
    )

    result = MatchingEngine().match(
        contract,
        purchase_order,
        invoice,
    )

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 1

    exception = result.exceptions[0]

    assert exception.type == "PRICE_MISMATCH"
    assert exception.item_code == "ITM-001"
    assert exception.field == "unit_price"
    assert exception.expected["min"] == 245.0
    assert exception.expected["max"] == 255.0
    assert exception.actual == 256.0


# ============================================================
# NEGATIVE — INVOICE PRICE ABOVE PO
# ============================================================

def test_full_validation_detects_invoice_price_above_po():
    """
    PO = 250
    Invoice = 251
    """

    contract, purchase_order, invoice = create_documents(
        po_price=250.0,
        invoice_price=251.0,
    )

    result = MatchingEngine().match(
        contract,
        purchase_order,
        invoice,
    )

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 1

    exception = result.exceptions[0]

    assert exception.type == "PRICE_MISMATCH"
    assert exception.item_code == "ITM-001"
    assert exception.field == "unit_price"
    assert exception.expected == 250.0
    assert exception.actual == 251.0
    assert exception.tolerance is None


# ============================================================
# NEGATIVE — MULTIPLE INDEPENDENT EXCEPTIONS
# ============================================================

def test_full_validation_collects_all_exceptions():
    """
    Deliberately introduce failures in every validation category.

    Relationships:
        PO → wrong Contract
        Invoice → wrong PO

    Quantity:
        Contract = 100
        PO = 106
        Invoice = 107

    Price:
        Contract = 250
        PO = 256
        Invoice = 257

    Expected:
        2 relationship exceptions
        2 quantity exceptions
        2 price exceptions

        Total = 6 exceptions
    """

    contract, purchase_order, invoice = create_documents(
        po_quantity=106,
        invoice_quantity=107,
        po_price=256.0,
        invoice_price=257.0,
        contract_reference="CON-2026-999",
        invoice_po_reference="PO-2026-9999",
    )

    result = MatchingEngine().match(
        contract,
        purchase_order,
        invoice,
    )

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 6

    exception_types = [
        exception.type
        for exception in result.exceptions
    ]

    assert exception_types.count(
        "CONTRACT_REFERENCE_MISMATCH"
    ) == 1

    assert exception_types.count(
        "PO_REFERENCE_MISMATCH"
    ) == 1

    assert exception_types.count(
        "QUANTITY_MISMATCH"
    ) == 2

    assert exception_types.count(
        "PRICE_MISMATCH"
    ) == 2


# ============================================================
# TRACEABILITY
# ============================================================

def test_full_validation_preserves_exception_source():
    """
    Verify that the matching layer preserves the source
    reference of a failing document value.
    """

    from app.models.source_reference import SourceReference

    contract, purchase_order, invoice = create_documents(
        po_quantity=106,
        invoice_quantity=106,
    )

    purchase_order.line_items[0].source = SourceReference(
        document_id="PO-2026-1001",
        document_path=(
            "data/purchase_orders/"
            "purchase_order_PO-2026-1001.pdf"
        ),
        page_number=1,
        polygon=[
            {"x": 1.0, "y": 1.0},
            {"x": 2.0, "y": 1.0},
            {"x": 2.0, "y": 2.0},
            {"x": 1.0, "y": 2.0},
        ],
    )

    result = MatchingEngine().match(
        contract,
        purchase_order,
        invoice,
    )

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 1

    exception = result.exceptions[0]

    assert exception.type == "QUANTITY_MISMATCH"
    assert exception.source is not None
    assert exception.source.document_id == "PO-2026-1001"
    assert (
        exception.source.document_path
        == (
            "data/purchase_orders/"
            "purchase_order_PO-2026-1001.pdf"
        )
    )
    assert exception.source.page_number == 1
    assert len(exception.source.polygon) == 4
    