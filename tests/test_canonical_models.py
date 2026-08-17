from app.models.contract import Contract
from app.models.invoice import Invoice
from app.models.line_item import LineItem
from app.models.purchase_order import PurchaseOrder
from app.models.source_reference import SourceReference


def create_source():
    return SourceReference(
        document_id="DOC-001",
        document_path="document.pdf",
        page_number=1,
        polygon=[
            {"x": 1.0, "y": 1.0},
            {"x": 2.0, "y": 1.0},
            {"x": 2.0, "y": 2.0},
            {"x": 1.0, "y": 2.0},
        ],
    )


def test_source_reference():

    source = create_source()

    assert source.document_id == "DOC-001"
    assert source.page_number == 1
    assert len(source.polygon) == 4


def test_line_item():

    source = create_source()

    item = LineItem(
        item_code="ITM-001",
        description="Industrial Safety Gloves",
        quantity=100.0,
        unit="Pair",
        unit_price=250.0,
        tax=18.0,
        source=source,
    )

    assert item.item_code == "ITM-001"
    assert item.description == "Industrial Safety Gloves"
    assert item.quantity == 100.0
    assert item.unit == "Pair"
    assert item.unit_price == 250.0
    assert item.tax == 18.0
    assert item.source == source


def test_contract():

    contract = Contract(
        contract_id="CON-001",
        contract_number="CON-2026-001",
        contract_date="01 August 2026",
        buyer="ABC Manufacturing Pvt. Ltd.",
        supplier="Global Office Supplies Ltd.",
        contract_validity=(
            "01 August 2026 to 31 December 2026"
        ),
        payment_terms="Net 30 days from invoice date.",
        quantity_tolerance="+5%",
        price_tolerance="±2%",
        invoice_rule=(
            "Invoice must reference a valid Purchase Order "
            "issued under this contract."
        ),
        line_items=[
            LineItem(
                item_code="ITM-001",
                description="Industrial Safety Gloves",
                quantity=100.0,
                unit="Pair",
                unit_price=250.0,
                tax=18.0,
                source=create_source(),
            )
        ],
        source=create_source(),
    )

    assert contract.contract_id == "CON-001"
    assert contract.contract_number == "CON-2026-001"
    assert contract.buyer == "ABC Manufacturing Pvt. Ltd."
    assert contract.supplier == "Global Office Supplies Ltd."
    assert contract.quantity_tolerance == "+5%"
    assert contract.price_tolerance == "±2%"
    assert len(contract.line_items) == 1


def test_purchase_order():

    po = PurchaseOrder(
        po_id="PO-ID-001",
        po_number="PO-2026-1001",
        contract_reference="CON-2026-001",
        po_date="05 August 2026",
        buyer="ABC Manufacturing Pvt. Ltd.",
        supplier="Global Office Supplies Ltd.",
        line_items=[
            LineItem(
                item_code="ITM-001",
                description="Industrial Safety Gloves",
                quantity=100.0,
                unit="Pair",
                unit_price=250.0,
                tax=18.0,
                source=create_source(),
            )
        ],
        source=create_source(),
    )

    assert po.po_id == "PO-ID-001"
    assert po.po_number == "PO-2026-1001"
    assert po.contract_reference == "CON-2026-001"
    assert len(po.line_items) == 1


def test_invoice():

    invoice = Invoice(
        invoice_id="INV-ID-001",
        invoice_number="INV-2026-5001",
        purchase_order_reference="PO-2026-1001",
        invoice_date="10 August 2026",
        due_date="09 September 2026",
        vendor="Global Office Supplies Ltd.",
        customer="ABC Manufacturing Pvt. Ltd.",
        subtotal=65000.0,
        total_tax=11700.0,
        total=76700.0,
        line_items=[
            LineItem(
                item_code="ITM-001",
                description="Industrial Safety Gloves",
                quantity=100.0,
                unit="Pair",
                unit_price=250.0,
                amount=25000.0,
                source=create_source(),
            )
        ],
        source=create_source(),
    )

    assert invoice.invoice_id == "INV-ID-001"
    assert invoice.invoice_number == "INV-2026-5001"
    assert invoice.purchase_order_reference == "PO-2026-1001"
    assert invoice.total == 76700.0
    assert len(invoice.line_items) == 1


def test_complete_document_relationship():

    source = create_source()

    line_item = LineItem(
        item_code="ITM-001",
        quantity=100.0,
        unit_price=250.0,
        source=source,
    )

    contract = Contract(
        contract_id="CON-001",
        contract_number="CON-2026-001",
        line_items=[line_item],
        source=source,
    )

    po = PurchaseOrder(
        po_id="PO-ID-001",
        po_number="PO-2026-1001",
        contract_reference=contract.contract_number,
        line_items=[line_item],
        source=source,
    )

    invoice = Invoice(
        invoice_id="INV-ID-001",
        invoice_number="INV-2026-5001",
        purchase_order_reference=po.po_number,
        line_items=[line_item],
        source=source,
    )

    assert po.contract_reference == contract.contract_number
    assert (
        invoice.purchase_order_reference
        == po.po_number
    )

    assert (
        contract.line_items[0].item_code
        == po.line_items[0].item_code
        == invoice.line_items[0].item_code
    )