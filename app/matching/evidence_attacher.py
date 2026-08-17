from typing import Any, Dict

from app.capabilities.evidence_generator import EvidenceGenerator
from app.models.validation_result import (
    ValidationException,
)


class EvidenceAttacher:
    """
    Attaches visual evidence to validation exceptions.

    This class adapts the matching domain model to the current
    EvidenceGenerator interface.

    Matching logic remains completely independent from the
    document evidence implementation.
    """

    def __init__(
        self,
        evidence_generator: EvidenceGenerator | None = None,
    ):
        self.evidence_generator = (
            evidence_generator or EvidenceGenerator()
        )

    def attach(
        self,
        exception: ValidationException,
    ) -> ValidationException:

        if exception.source is None:
            return exception

        if not exception.field:
            return exception

        source = exception.source

        evidence_reference: Dict[str, Any] = {
            "document_path": source.document_path,
            "field": exception.field,
            "page_number": source.page_number,
            "polygon": source.polygon,
        }

        evidence_result = (
            self.evidence_generator.generate_evidence(
                exception_type=exception.type,
                evidence_references=[
                    evidence_reference
                ],
            )
        )

        exception.evidence = evidence_result["evidence"]

        return exception