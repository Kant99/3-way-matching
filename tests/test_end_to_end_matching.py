from pathlib import Path

from app.capabilities.evidence_generator import EvidenceGenerator
from app.matching.matching_engine import MatchingEngine
from app.models.contract import Contract
from app.models.invoice import Invoice
from app.models.line_item import LineItem
from app.models.purchase_order import PurchaseOrder
from app.models.source_reference import SourceReference


TEST_PDF = r"data\invoices\invoice_INV-2026-5001.pdf"


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
            )
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
            )
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
            )
        ],
    )

    return contract, purchase_order, invoice


def create_source(document_id, document_path=TEST_PDF):
    return SourceReference(
        document_id=document_id,
        document_path=document_path,
        page_number=1,
        polygon=[
            {"x": 1.0, "y": 1.0},
            {"x": 2.0, "y": 1.0},
            {"x": 2.0, "y": 2.0},
            {"x": 1.0, "y": 2.0},
        ],
    )


# ============================================================
# END-TO-END POSITIVE CASE
# ============================================================

def test_end_to_end_valid_three_way_match(tmp_path):
    contract, purchase_order, invoice = create_documents()

    evidence_generator = EvidenceGenerator(
        output_dir=str(tmp_path / "evidence")
    )

    engine = MatchingEngine(
        evidence_generator=evidence_generator
    )

    result = engine.match(
        contract,
        purchase_order,
        invoice,
    )

    assert result.status == "PASS"
    assert result.exceptions == []


# ============================================================
# END-TO-END NEGATIVE CASE
# ============================================================

def test_end_to_end_invalid_three_way_match_with_evidence(
    tmp_path,
):
    """
    Contract:
        Quantity = 100
        Price = 250

    PO:
        Quantity = 106
        Price = 256

    Invoice:
        Quantity = 107
        Price = 257

    Expected:
        Contract → PO quantity       FAIL
        PO → Invoice quantity        FAIL
        Contract → PO price          FAIL
        PO → Invoice price           FAIL

        Total = 4 exceptions

    Evidence should be generated for exceptions
    that contain SourceReference.
    """

    contract, purchase_order, invoice = create_documents(
        po_quantity=106,
        invoice_quantity=107,
        po_price=256.0,
        invoice_price=257.0,
    )

    # Add source information to the failing PO values.
    purchase_order.line_items[0].source = create_source(
        "PO-2026-1001"
    )

    # Add source information to the failing Invoice values.
    invoice.line_items[0].source = create_source(
        "INV-2026-5001"
    )

    evidence_generator = EvidenceGenerator(
        output_dir=str(tmp_path / "evidence")
    )

    engine = MatchingEngine(
        evidence_generator=evidence_generator
    )

    result = engine.match(
        contract,
        purchase_order,
        invoice,
    )

    # --------------------------------------------------------
    # Final validation result
    # --------------------------------------------------------

    assert result.status == "EXCEPTION"
    assert len(result.exceptions) == 4

    # --------------------------------------------------------
    # Verify exception types
    # --------------------------------------------------------

    exception_types = [
        exception.type
        for exception in result.exceptions
    ]

    assert exception_types.count(
        "QUANTITY_MISMATCH"
    ) == 2

    assert exception_types.count(
        "PRICE_MISMATCH"
    ) == 2

    # --------------------------------------------------------
    # Verify quantity exceptions
    # --------------------------------------------------------

    quantity_exceptions = [
        exception
        for exception in result.exceptions
        if exception.type == "QUANTITY_MISMATCH"
    ]

    assert len(quantity_exceptions) == 2

    for exception in quantity_exceptions:
        assert exception.field == "quantity"
        assert exception.source is not None
        assert len(exception.evidence) == 1

        evidence = exception.evidence[0]

        assert evidence["field"] == "quantity"

        snip_path = Path(
            evidence["snip_path"]
        )

        assert snip_path.exists()
        assert snip_path.is_file()
        assert snip_path.suffix.lower() == ".png"

    # --------------------------------------------------------
    # Verify price exceptions
    # --------------------------------------------------------

    price_exceptions = [
        exception
        for exception in result.exceptions
        if exception.type == "PRICE_MISMATCH"
    ]

    assert len(price_exceptions) == 2

    for exception in price_exceptions:
        assert exception.field == "unit_price"
        assert exception.source is not None
        assert len(exception.evidence) == 1

        evidence = exception.evidence[0]

        assert evidence["field"] == "unit_price"

        snip_path = Path(
            evidence["snip_path"]
        )

        assert snip_path.exists()
        assert snip_path.is_file()
        assert snip_path.suffix.lower() == ".png"