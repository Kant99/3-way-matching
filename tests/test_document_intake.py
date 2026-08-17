from app.capabilities.document_intake import DocumentIntake


def test_document_intake_discovers_documents():

    intake = DocumentIntake("data")

    documents = intake.discover_documents()

    assert "contracts" in documents
    assert "purchase_orders" in documents
    assert "invoices" in documents

    assert len(documents["contracts"]) >= 1
    assert len(documents["purchase_orders"]) >= 1
    assert len(documents["invoices"]) >= 1


def test_document_metadata():

    intake = DocumentIntake("data")

    documents = intake.discover_documents()

    contract = documents["contracts"][0]
    purchase_order = documents["purchase_orders"][0]
    invoice = documents["invoices"][0]

    for document in [contract, purchase_order, invoice]:
        assert document["document_id"]
        assert document["filename"]
        assert document["path"]
        assert document["document_type"]
        assert document["file_extension"]
        assert document["file_size"] > 0


def test_document_types():

    intake = DocumentIntake("data")

    documents = intake.discover_documents()

    assert documents["contracts"][0]["document_type"] == "CONTRACT"
    assert documents["purchase_orders"][0]["document_type"] == "PURCHASE_ORDER"
    assert documents["invoices"][0]["document_type"] == "INVOICE"


def test_document_id_is_deterministic():

    intake = DocumentIntake("data")

    first_run = intake.discover_documents()
    second_run = intake.discover_documents()

    assert (
        first_run["contracts"][0]["document_id"]
        == second_run["contracts"][0]["document_id"]
    )

def test_document_classification():

    intake = DocumentIntake("data")

    assert intake.classify_document("contracts") == "CONTRACT"
    assert intake.classify_document("purchase_orders") == "PURCHASE_ORDER"
    assert intake.classify_document("invoices") == "INVOICE"


def test_invalid_document_classification():

    intake = DocumentIntake("data")

    try:
        intake.classify_document("unknown")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Unsupported document category" in str(exc)