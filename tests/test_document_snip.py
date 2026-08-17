from pathlib import Path

from app.capabilities.document_snip import DocumentSnip


CONTRACT_PATH = (
    "data/contracts/contract_CON-2026-001.pdf"
)

OUTPUT_PATH = (
    "outputs/evidence/test_contract_quantity.png"
)


def test_document_snip():

    snip = DocumentSnip()

    output = snip.create_snip(
        document_path=CONTRACT_PATH,
        page_number=1,
        polygon=[
            {"x": 3.7254, "y": 3.7496},
            {"x": 4.6725, "y": 3.7496},
            {"x": 4.6725, "y": 3.9993},
            {"x": 3.7316, "y": 3.9993},
        ],
        output_path=OUTPUT_PATH,
    )

    assert Path(output).exists()
    assert Path(output).stat().st_size > 0


def test_document_snip_missing_file():

    snip = DocumentSnip()

    try:
        snip.create_snip(
            document_path="data/contracts/does_not_exist.pdf",
            page_number=1,
            polygon=[
                {"x": 1.0, "y": 1.0},
                {"x": 2.0, "y": 1.0},
                {"x": 2.0, "y": 2.0},
                {"x": 1.0, "y": 2.0},
            ],
            output_path=OUTPUT_PATH,
        )

        assert False, "Expected FileNotFoundError"

    except FileNotFoundError:
        pass


def test_document_snip_invalid_page():

    snip = DocumentSnip()

    try:
        snip.create_snip(
            document_path=CONTRACT_PATH,
            page_number=99,
            polygon=[
                {"x": 1.0, "y": 1.0},
                {"x": 2.0, "y": 1.0},
                {"x": 2.0, "y": 2.0},
                {"x": 1.0, "y": 2.0},
            ],
            output_path=OUTPUT_PATH,
        )

        assert False, "Expected ValueError"

    except ValueError as exc:
        assert "Page 99 does not exist" in str(exc)