from app.capabilities.contract_extractor import ContractExtractor


CONTRACT_PATH = (
    "data/contracts/contract_CON-2026-001.pdf"
)


def test_contract_extraction():

    extractor = ContractExtractor()

    contract = extractor.extract_contract(
        CONTRACT_PATH
    )

    assert contract["document_path"].endswith(
        "contract_CON-2026-001.pdf"
    )

    assert contract["contract_number"]["value"] == "CON-2026-001"
    assert contract["contract_date"]["value"] == "01 August 2026"

    assert (
        contract["buyer"]["value"]
        == "ABC Manufacturing Pvt. Ltd."
    )

    assert (
        contract["supplier"]["value"]
        == "Global Office Supplies Ltd."
    )

    assert (
        contract["contract_validity"]["value"]
        == "01 August 2026 to 31 December 2026"
    )

    assert (
        contract["payment_terms"]["value"]
        == "Net 30 days from invoice date."
    )

    assert (
        contract["quantity_tolerance"]["value"]
        == "+5%"
    )

    assert (
        contract["price_tolerance"]["value"]
        == "±2%"
    )

    assert (
        contract["invoice_rule"]["value"]
        == (
            "Invoice must reference a valid Purchase Order "
            "issued under this contract."
        )
    )


def test_contract_line_items():

    extractor = ContractExtractor()

    contract = extractor.extract_contract(
        CONTRACT_PATH
    )

    items = contract["line_items"]

    assert len(items) == 3

    assert items[0]["item_code"]["value"] == "ITM-001"
    assert items[0]["description"]["value"] == (
        "Industrial Safety Gloves"
    )
    assert items[0]["quantity"]["value"] == "100"
    assert items[0]["unit"]["value"] == "Pair"
    assert items[0]["unit_price"]["value"] == "250.00"

    assert items[1]["item_code"]["value"] == "ITM-002"
    assert items[1]["quantity"]["value"] == "50"
    assert items[1]["unit_price"]["value"] == "800.00"

    assert items[2]["item_code"]["value"] == "ITM-003"
    assert items[2]["quantity"]["value"] == "75"
    assert items[2]["unit_price"]["value"] == "400.00"


def test_contract_source_locations():

    extractor = ContractExtractor()

    contract = extractor.extract_contract(
        CONTRACT_PATH
    )

    assert len(
        contract["contract_number"]["source"]
    ) > 0

    assert len(
        contract["quantity_tolerance"]["source"]
    ) > 0

    assert len(
        contract["invoice_rule"]["source"]
    ) > 0

    first_item = contract["line_items"][0]

    for field_name in [
        "item_code",
        "description",
        "quantity",
        "unit",
        "unit_price",
        "tax",
    ]:
        source = first_item[field_name]["source"]

        assert len(source) > 0
        assert source[0]["page_number"] >= 1
        assert len(source[0]["polygon"]) > 0


def test_contract_extraction_missing_file():

    extractor = ContractExtractor()

    try:
        extractor.extract_contract(
            "data/contracts/does_not_exist.pdf"
        )
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass