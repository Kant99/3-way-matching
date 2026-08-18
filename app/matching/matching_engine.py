from pathlib import Path

from app.models.contract import Contract
from app.models.purchase_order import PurchaseOrder
from app.models.invoice import Invoice
from app.models.validation_result import (
    ValidationException,
    ValidationResult,
)

from app.matching.relationship_validator import (
    RelationshipValidator,
)
from app.matching.line_item_matcher import (
    LineItemMatcher,
)
from app.matching.quantity_validator import (
    QuantityValidator,
)
from app.matching.price_validator import (
    PriceValidator,
)
from app.capabilities.evidence_generator import (
    EvidenceGenerator,
)


class MatchingEngine:
    def __init__(
        self,
        evidence_generator: EvidenceGenerator | None = None,
    ):
        self.relationship_validator = (
            RelationshipValidator()
        )

        self.line_item_matcher = (
            LineItemMatcher()
        )

        self.quantity_validator = (
            QuantityValidator()
        )

        self.price_validator = (
            PriceValidator()
        )

        self.evidence_generator = (
            evidence_generator
            or EvidenceGenerator()
        )

    def match(
        self,
        contract: Contract,
        purchase_order: PurchaseOrder,
        invoice: Invoice,
    ) -> ValidationResult:

        exceptions: list[ValidationException] = []

        # --------------------------------------------------
        # 1. Document relationship validation
        # --------------------------------------------------

        relationship_result = (
            self.relationship_validator.validate(
                contract,
                purchase_order,
                invoice,
            )
        )

        exceptions.extend(
            relationship_result.exceptions
        )

        # --------------------------------------------------
        # 2. Line-item matching
        # --------------------------------------------------

        line_match_result = (
            self.line_item_matcher.match(
                contract,
                purchase_order,
                invoice,
            )
        )

        line_matches = (
            line_match_result["matches"]
        )

        # --------------------------------------------------
        # 3. Quantity validation
        # --------------------------------------------------

        quantity_result = (
            self.quantity_validator.validate(
                contract,
                purchase_order,
                invoice,
                line_matches,
            )
        )

        exceptions.extend(
            quantity_result.exceptions
        )

        # --------------------------------------------------
        # 4. Price validation
        # --------------------------------------------------

        price_result = (
            self.price_validator.validate(
                contract,
                purchase_order,
                invoice,
                line_matches,
            )
        )

        exceptions.extend(
            price_result.exceptions
        )

        # --------------------------------------------------
        # 5. Attach visual evidence
        # --------------------------------------------------

        for exception in exceptions:

            if exception.source is None:
                continue

            source = exception.source

            if not source.document_path:
                continue

            if source.page_number is None:
                continue

            if not source.polygon:
                continue

            document_name = Path(
                source.document_path
            ).stem

            output_name = (
                f"{document_name}_"
                f"{exception.item_code or exception.type}_"
                f"{exception.field or 'record'}_"
                f"whole_row.png"
            )

            evidence_result = (
                self.evidence_generator
                .generate_row_evidence_from_source(
                    document_path=(
                        source.document_path
                    ),
                    page_number=(
                        source.page_number
                    ),
                    polygon=source.polygon,
                    output_name=output_name,
                )
            )

            exception.evidence = [
                {
                    "document_path": (
                        evidence_result[
                            "document_path"
                        ]
                    ),
                    "field": "whole_row",
                    "page_number": (
                        evidence_result[
                            "page_number"
                        ]
                    ),
                    "snip_path": (
                        evidence_result[
                            "snip_path"
                        ]
                    ),
                }
            ]

        # --------------------------------------------------
        # 6. Final result
        # --------------------------------------------------

        return ValidationResult(
            status=(
                "EXCEPTION"
                if exceptions
                else "PASS"
            ),
            exceptions=exceptions,
        )