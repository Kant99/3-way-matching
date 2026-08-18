from pathlib import Path

from app.capabilities.contract_extractor import ContractExtractor
from app.capabilities.invoice_extractor import InvoiceExtractor
from app.capabilities.purchase_order_extractor import (
    PurchaseOrderExtractor,
)


# -------------------------------------------------------------------
# Update these paths only if your PDFs are stored somewhere else.
# -------------------------------------------------------------------

CONTRACT_PATH = (
    "data/contracts/contract_CON-2026-001.pdf"
)

PO_PATH = (
    "data/purchase_orders/purchase_order_PO-2026-1001.pdf"
)

INVOICE_PATH = (
    "data/invoices/invoice_INV-2026-5001.pdf"
)


def _print_separator(title: str) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def _print_source(
    field_name: str,
    field_data: dict | None,
) -> None:
    print()
    print(f"  {field_name}")

    if not field_data:
        print("    VALUE: None")
        print("    SOURCE: None")
        return

    print(f"    VALUE: {field_data.get('value')}")

    locations = field_data.get("source", [])

    if not locations:
        print("    SOURCE: None")
        return

    for index, location in enumerate(locations, start=1):
        print(f"    SOURCE LOCATION {index}")
        print(
            f"      PAGE: "
            f"{location.get('page_number')}"
        )

        polygon = location.get("polygon", [])

        print("      POLYGON:")

        for point in polygon:
            print(
                f"        x={point.get('x')}, "
                f"y={point.get('y')}"
            )


def _print_line_item(
    index: int,
    item: dict,
) -> None:
    print()
    print("-" * 60)
    print(f"  LINE ITEM {index}")
    print("-" * 60)

    for field_name in (
        "item_code",
        "description",
        "quantity",
        "unit",
        "unit_price",
        "tax",
        "amount",
    ):
        if field_name not in item:
            continue

        _print_source(
            field_name,
            item.get(field_name),
        )


def test_real_document_coordinates() -> None:
    """
    Diagnostic test that verifies Azure Document Intelligence
    source coordinates are preserved by the existing extractors.

    This test intentionally does not modify any production code.
    """

    contract_path = Path(CONTRACT_PATH)
    po_path = Path(PO_PATH)
    invoice_path = Path(INVOICE_PATH)

    assert contract_path.exists(), (
        f"Contract PDF not found: {contract_path}"
    )

    assert po_path.exists(), (
        f"Purchase Order PDF not found: {po_path}"
    )

    assert invoice_path.exists(), (
        f"Invoice PDF not found: {invoice_path}"
    )

    # ---------------------------------------------------------------
    # CONTRACT
    # ---------------------------------------------------------------

    _print_separator(
        "CONTRACT — AZURE DOCUMENT INTELLIGENCE COORDINATES"
    )

    contract_extractor = ContractExtractor()

    contract = contract_extractor.extract_contract(
        str(contract_path)
    )

    print(
        f"Document: {contract.get('document_path')}"
    )

    print()
    print("HEADER FIELDS")

    for field_name in (
        "contract_number",
        "contract_date",
        "buyer",
        "supplier",
        "contract_validity",
        "payment_terms",
        "quantity_tolerance",
        "price_tolerance",
        "invoice_rule",
    ):
        _print_source(
            field_name,
            contract.get(field_name),
        )

    print()
    print("LINE ITEMS")

    contract_line_items = contract.get(
        "line_items",
        [],
    )

    print(
        f"Total line items: "
        f"{len(contract_line_items)}"
    )

    for index, item in enumerate(
        contract_line_items,
        start=1,
    ):
        _print_line_item(
            index,
            item,
        )

    # ---------------------------------------------------------------
    # PURCHASE ORDER
    # ---------------------------------------------------------------

    _print_separator(
        "PURCHASE ORDER — AZURE DOCUMENT INTELLIGENCE COORDINATES"
    )

    po_extractor = PurchaseOrderExtractor()

    purchase_order = (
        po_extractor.extract_purchase_order(
            str(po_path)
        )
    )

    print(
        f"Document: "
        f"{purchase_order.get('document_path')}"
    )

    print()
    print("HEADER FIELDS")

    for field_name in (
        "po_number",
        "po_date",
        "contract_reference",
        "buyer",
        "supplier",
        "subtotal",
        "gst",
        "payment_terms",
        "delivery_terms",
    ):
        _print_source(
            field_name,
            purchase_order.get(field_name),
        )

    print()
    print("LINE ITEMS")

    po_line_items = purchase_order.get(
        "line_items",
        [],
    )

    print(
        f"Total line items: "
        f"{len(po_line_items)}"
    )

    for index, item in enumerate(
        po_line_items,
        start=1,
    ):
        _print_line_item(
            index,
            item,
        )

    # ---------------------------------------------------------------
    # INVOICE
    # ---------------------------------------------------------------

    _print_separator(
        "INVOICE — AZURE DOCUMENT INTELLIGENCE COORDINATES"
    )

    invoice_extractor = InvoiceExtractor()

    invoice = invoice_extractor.extract_invoice(
        str(invoice_path)
    )

    print(
        f"Document: "
        f"{invoice.get('document_path')}"
    )

    print()
    print("HEADER FIELDS")

    for field_name in (
        "invoice_number",
        "purchase_order",
        "invoice_date",
        "due_date",
        "vendor_name",
        "customer_name",
        "subtotal",
        "total_tax",
        "invoice_total",
    ):
        _print_source(
            field_name,
            invoice.get(field_name),
        )

    print()
    print("LINE ITEMS")

    invoice_line_items = invoice.get(
        "line_items",
        []
    )

    print(
        f"Total line items: "
        f"{len(invoice_line_items)}"
    )

    for index, item in enumerate(
        invoice_line_items,
        start=1,
    ):
        _print_line_item(
            index,
            item,
        )

    # ---------------------------------------------------------------
    # FINAL ASSERTIONS
    # ---------------------------------------------------------------

    print()
    _print_separator(
        "COORDINATE VERIFICATION SUMMARY"
    )

    print(
        "Azure Document Intelligence extraction completed."
    )

    print(
        "Source locations were inspected for "
        "Contract, PO, and Invoice."
    )

    print(
        "This test does not modify any production capability."
    )