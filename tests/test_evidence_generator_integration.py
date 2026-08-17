from pathlib import Path

from app.capabilities.evidence_generator import EvidenceGenerator
from app.models.source_reference import SourceReference


def test_evidence_generator_creates_snip_from_source_reference(
    tmp_path,
):
    # Use an existing test PDF from your project.
    document_path = r"data\invoices\invoice_INV-2026-5001.pdf"

    source = SourceReference(
        document_id="INV-2026-5001",
        document_path=document_path,
        page_number=1,
        polygon=[
            {"x": 1.0, "y": 1.0},
            {"x": 2.0, "y": 1.0},
            {"x": 2.0, "y": 2.0},
            {"x": 1.0, "y": 2.0},
        ],
    )

    output_dir = tmp_path / "evidence"

    generator = EvidenceGenerator(
        output_dir=str(output_dir)
    )

    result = generator.generate_evidence(
        exception_type="QUANTITY_MISMATCH",
        evidence_references=[
            {
                "document_path": source.document_path,
                "field": "quantity",
                "page_number": source.page_number,
                "polygon": source.polygon,
            }
        ],
    )

    assert result["exception_type"] == "QUANTITY_MISMATCH"
    assert len(result["evidence"]) == 1

    evidence = result["evidence"][0]

    assert evidence["field"] == "quantity"

    snip_path = Path(
        evidence["snip_path"]
    )

    assert snip_path.exists()
    assert snip_path.is_file()
    assert snip_path.suffix.lower() == ".png"