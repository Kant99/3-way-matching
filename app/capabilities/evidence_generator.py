from pathlib import Path
from typing import Any, Dict, List

from app.capabilities.document_snip import DocumentSnip


class EvidenceGenerator:
    """
    Generates visual evidence for validation exceptions.

    This capability does not perform validation or matching.
    It only converts known source locations into visual snippets.
    """

    def __init__(
        self,
        document_snip: DocumentSnip | None = None,
        output_dir: str = "outputs/evidence",
    ):
        self.document_snip = document_snip or DocumentSnip()
        self.output_dir = Path(output_dir)

    def generate_evidence(
        self,
        exception_type: str,
        evidence_references: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate evidence snippets for supplied source references.
        """

        if not exception_type:
            raise ValueError(
                "exception_type cannot be empty"
            )

        if not evidence_references:
            raise ValueError(
                "evidence_references cannot be empty"
            )

        generated_evidence = []

        for index, reference in enumerate(
            evidence_references
        ):

            document_path = reference.get(
                "document_path"
            )

            field = reference.get("field")

            page_number = reference.get(
                "page_number"
            )

            polygon = reference.get(
                "polygon"
            )

            if not document_path:
                raise ValueError(
                    "Evidence reference requires document_path"
                )

            if not field:
                raise ValueError(
                    "Evidence reference requires field"
                )

            if page_number is None:
                raise ValueError(
                    "Evidence reference requires page_number"
                )

            if not polygon:
                raise ValueError(
                    "Evidence reference requires polygon"
                )

            document_name = Path(
                document_path
            ).stem

            output_path = (
                self.output_dir
                / f"{document_name}_{field}_{index}.png"
            )

            snip_path = self.document_snip.create_snip(
                document_path=document_path,
                page_number=page_number,
                polygon=polygon,
                output_path=str(output_path),
            )

            generated_evidence.append(
                {
                    "document_path": document_path,
                    "field": field,
                    "page_number": page_number,
                    "snip_path": snip_path,
                }
            )

        return {
            "exception_type": exception_type,
            "evidence": generated_evidence,
        }