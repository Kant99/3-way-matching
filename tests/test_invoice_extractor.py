from app.capabilities.invoice_extractor import InvoiceExtractor


INVOICE_PATH = (
    "data/invoices/invoice_INV-2026-5001.pdf"
)

from app.capabilities.invoice_extractor import InvoiceExtractor


def test_invoice_field_source_shape():

    extractor = InvoiceExtractor()

    invoice = extractor.extract_invoice(
        "data/invoices/invoice_INV-2026-5001.pdf"
    )

    assert invoice["invoice_number"] is not None




def test_invoice_extraction():

    extractor = InvoiceExtractor()

    invoice = extractor.extract_invoice(INVOICE_PATH)

    assert invoice["document_path"].endswith(
        "invoice_INV-2026-5001.pdf"
    )

    assert invoice["invoice_number"] is not None
    assert invoice["purchase_order"] is not None

    assert len(invoice["line_items"]) >= 1


def test_invoice_line_items():

    extractor = InvoiceExtractor()

    invoice = extractor.extract_invoice(INVOICE_PATH)

    first_item = invoice["line_items"][0]

    assert first_item["description"] is not None
    assert first_item["quantity"] is not None
    assert first_item["unit_price"] is not None
    assert first_item["amount"] is not None


def test_invoice_extraction_missing_file():

    extractor = InvoiceExtractor()

    try:
        extractor.extract_invoice(
            "data/invoices/does_not_exist.pdf"
        )
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass