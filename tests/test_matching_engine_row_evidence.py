from pathlib import Path

from app.capabilities.evidence_generator import (
    EvidenceGenerator,
)
from app.matching.matching_engine import (
    MatchingEngine,
)
from app.models.contract import Contract
from app.models.invoice import Invoice
from app.models.line_item import LineItem
from app.models.purchase_order import PurchaseOrder
from app.models.source_reference import (
    SourceReference,
)


INVOICE_PATH = (
    "data/invoices/invoice_INV-2026-5001.pdf"
)


def test_matching_engine_generates_whole_row_evidence():
    invoice_path = Path(
        INVOICE_PATH
    )

    assert invoice_path.exists()

    source = SourceReference(
        document_id="INV-2026-5001",
        document_path=str(
            invoice_path
        ),
        page_number=1,
        polygon=[
            {"x": 3.9589, "y": 3.6201},
            {"x": 4.1377, "y": 3.6195},
            {"x": 4.1377, "y": 3.7199},
            {"x": 3.9588, "y": 3.7201},
        ],
    )

    contract = Contract(
        contract_id="CON-2026-001",
        contract_number="CON-2026-001",
        price_tolerance="±2%",
        quantity_tolerance="+5%",
        line_items=[
            LineItem(
                item_code="ITM-001",
                description="Industrial Safety Gloves",
                quantity=100,
                unit="Pair",
                unit_price=250,
                tax="18%",
                amount=25000,
                source=source,
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
                unit_price=250,
                tax="18%",
                amount=25000,
                source=source,
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
                unit_price=260,
                tax="18%",
                amount=26000,
                source=source,
            )
        ],
    )

    evidence_generator = EvidenceGenerator(
        output_dir="outputs/evidence"
    )

    engine = MatchingEngine(
        evidence_generator=evidence_generator
    )

    result = engine.match(
        contract,
        purchase_order,
        invoice,
    )

    assert result.status == "EXCEPTION"

    price_exceptions = [
        exception
        for exception in result.exceptions
        if exception.type == "PRICE_MISMATCH"
    ]

    assert price_exceptions

    exception = price_exceptions[0]

    assert exception.item_code == "ITM-001"
    assert exception.field == "unit_price"

    assert len(exception.evidence) == 1

    evidence = exception.evidence[0]

    assert evidence["field"] == "whole_row"
    assert evidence["page_number"] == 1

    snip_path = Path(
        evidence["snip_path"]
    )

    assert snip_path.exists()
    assert snip_path.is_file()

    print()
    print(
        f"Generated whole-row evidence: "
        f"{snip_path}"
    )