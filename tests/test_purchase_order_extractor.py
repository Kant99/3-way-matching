from app.capabilities.purchase_order_extractor import (
    PurchaseOrderExtractor,
)


PO_PATH = (
    "data/purchase_orders/"
    "purchase_order_PO-2026-1001.pdf"
)


def test_purchase_order_extraction():

    extractor = PurchaseOrderExtractor()

    po = extractor.extract_purchase_order(
        PO_PATH
    )

    assert po["po_number"]["value"] == (
        "PO-2026-1001"
    )

    assert po["po_date"]["value"] == (
        "05 August 2026"
    )

    assert po["contract_reference"]["value"] == (
        "CON-2026-001"
    )

    assert po["buyer"]["value"] == (
        "ABC Manufacturing Pvt. Ltd."
    )

    assert po["supplier"]["value"] == (
        "Global Office Supplies Ltd."
    )


def test_purchase_order_line_items():

    extractor = PurchaseOrderExtractor()

    po = extractor.extract_purchase_order(
        PO_PATH
    )

    items = po["line_items"]

    assert len(items) == 2

    assert items[0]["item_code"]["value"] == "ITM-001"
    assert (
        items[0]["description"]["value"]
        == "Industrial Safety Gloves"
    )
    assert items[0]["quantity"]["value"] == "100"
    assert items[0]["unit"]["value"] == "Pair"
    assert items[0]["unit_price"]["value"] == "250.00"
    assert items[0]["amount"]["value"] == "25,000.00"

    assert items[1]["item_code"]["value"] == "ITM-002"
    assert items[1]["quantity"]["value"] == "50"
    assert items[1]["unit"]["value"] == "Each"
    assert items[1]["unit_price"]["value"] == "800.00"
    assert items[1]["amount"]["value"] == "40,000.00"


def test_purchase_order_terms():

    extractor = PurchaseOrderExtractor()

    po = extractor.extract_purchase_order(
        PO_PATH
    )

    assert po["subtotal"]["value"] == "65,000.00"
    assert po["gst"]["value"] == "18%"
    assert po["payment_terms"]["value"] == (
        "Net 30 days"
    )
    assert po["delivery_terms"]["value"] == (
        "As per contract terms"
    )


def test_purchase_order_source_locations():

    extractor = PurchaseOrderExtractor()

    po = extractor.extract_purchase_order(
        PO_PATH
    )

    assert len(
        po["po_number"]["source"]
    ) > 0

    first_item = po["line_items"][0]

    for field_name in [
        "item_code",
        "description",
        "quantity",
        "unit",
        "unit_price",
        "amount",
    ]:
        assert len(
            first_item[field_name]["source"]
        ) > 0

        source = first_item[
            field_name
        ]["source"][0]

        assert source["page_number"] == 1
        assert len(source["polygon"]) > 0


def test_purchase_order_missing_file():

    extractor = PurchaseOrderExtractor()

    try:
        extractor.extract_purchase_order(
            "data/purchase_orders/does_not_exist.pdf"
        )

        assert False, (
            "Expected FileNotFoundError"
        )

    except FileNotFoundError:
        pass