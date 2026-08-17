from app.capabilities.table_extraction import TableExtractor


def test_table_extraction_contract():

    extractor = TableExtractor()

    tables = extractor.extract_tables(
        "data/contracts/contract_CON-2026-001.pdf"
    )

    assert len(tables) >= 1

    table = tables[0]

    assert table["table_index"] == 0
    assert table["row_count"] > 0
    assert table["column_count"] > 0
    assert len(table["cells"]) > 0


def test_table_cells_contain_source_location():

    extractor = TableExtractor()

    tables = extractor.extract_tables(
        "data/contracts/contract_CON-2026-001.pdf"
    )

    cells_with_location = [
        cell
        for table in tables
        for cell in table["cells"]
        if cell["bounding_regions"]
    ]

    assert len(cells_with_location) > 0

    first_cell = cells_with_location[0]

    region = first_cell["bounding_regions"][0]

    assert region["page_number"] >= 1
    assert len(region["polygon"]) > 0


def test_table_extraction_missing_file():

    extractor = TableExtractor()

    try:
        extractor.extract_tables(
            "data/contracts/does_not_exist.pdf"
        )
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass