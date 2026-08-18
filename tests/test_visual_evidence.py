from pathlib import Path

from app.capabilities.document_snip import DocumentSnip
from app.capabilities.invoice_extractor import InvoiceExtractor


INVOICE_PATH = (
    "data/invoices/invoice_INV-2026-5001.pdf"
)

OUTPUT_DIR = Path(
    "outputs/evidence_debug"
)


def build_row_polygon(line_item: dict) -> list[dict]:
    """
    Combine all field polygons belonging to one line item
    into one bounding rectangle.
    """

    all_points = []

    fields = (
        "item_code",
        "description",
        "quantity",
        "unit",
        "unit_price",
        "tax",
        "amount",
    )

    for field_name in fields:
        field = line_item.get(field_name)

        if not field:
            continue

        locations = field.get("source", [])

        for location in locations:
            polygon = location.get("polygon", [])

            for point in polygon:
                x = point.get("x")
                y = point.get("y")

                if x is None or y is None:
                    continue

                all_points.append(
                    {
                        "x": x,
                        "y": y,
                    }
                )

    if not all_points:
        return []

    min_x = min(
        point["x"]
        for point in all_points
    )

    max_x = max(
        point["x"]
        for point in all_points
    )

    min_y = min(
        point["y"]
        for point in all_points
    )

    max_y = max(
        point["y"]
        for point in all_points
    )

    return [
        {
            "x": min_x,
            "y": min_y,
        },
        {
            "x": max_x,
            "y": min_y,
        },
        {
            "x": max_x,
            "y": max_y,
        },
        {
            "x": min_x,
            "y": max_y,
        },
    ]


def get_row_page_number(line_item: dict) -> int | None:
    """
    Get the page number for the line item.

    For the current POC, all fields in a row are expected
    to belong to the same page.
    """

    fields = (
        "item_code",
        "description",
        "quantity",
        "unit",
        "unit_price",
        "tax",
        "amount",
    )

    for field_name in fields:
        field = line_item.get(field_name)

        if not field:
            continue

        locations = field.get("source", [])

        if locations:
            return locations[0].get(
                "page_number"
            )

    return None


def test_generate_whole_invoice_rows() -> None:
    """
    Generate one PNG for each complete invoice line item.
    """

    invoice_path = Path(INVOICE_PATH)

    assert invoice_path.exists(), (
        f"Invoice not found: {invoice_path}"
    )

    extractor = InvoiceExtractor()

    invoice = extractor.extract_invoice(
        str(invoice_path)
    )

    document_snip = DocumentSnip()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    generated_files = []

    line_items = invoice.get(
        "line_items",
        [],
    )

    for index, line_item in enumerate(
        line_items,
        start=1,
    ):
        item_code_data = line_item.get(
            "item_code",
            {},
        )

        item_code = item_code_data.get(
            "value",
            f"ROW-{index}",
        )

        row_polygon = build_row_polygon(
            line_item
        )

        if not row_polygon:
            print(
                f"Skipping {item_code}: "
                f"no polygon data."
            )
            continue

        page_number = get_row_page_number(
            line_item
        )

        if page_number is None:
            print(
                f"Skipping {item_code}: "
                f"no page number."
            )
            continue

        output_name = (
            f"invoice_"
            f"{item_code}_"
            f"full_row.png"
        )

        output_path = (
            OUTPUT_DIR / output_name
        )

        snip_path = (
            document_snip.create_snip(
                document_path=str(
                    invoice_path
                ),
                page_number=page_number,
                polygon=row_polygon,
                output_path=str(
                    output_path
                ),
            )
        )

        generated_files.append(
            snip_path
        )

        print()
        print("=" * 80)
        print(
            f"Generated row evidence: "
            f"{snip_path}"
        )
        print(
            f"Item: {item_code}"
        )
        print(
            f"Page: {page_number}"
        )
        print(
            f"Row polygon: {row_polygon}"
        )

    print()
    print("=" * 80)
    print("WHOLE ROW EVIDENCE GENERATION COMPLETE")
    print("=" * 80)

    print(
        f"Generated files: "
        f"{len(generated_files)}"
    )

    for file_path in generated_files:
        print(
            f"  {file_path}"
        )

    assert generated_files, (
        "No row evidence images were generated."
    )