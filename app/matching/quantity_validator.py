from app.models.contract import Contract
from app.models.purchase_order import PurchaseOrder
from app.models.invoice import Invoice
from app.models.validation_result import (
    ValidationException,
    ValidationResult,
)


class QuantityValidator:
    def validate(
        self,
        contract: Contract,
        purchase_order: PurchaseOrder,
        invoice: Invoice,
        line_matches: list[dict],
    ) -> ValidationResult:
        exceptions = []

        quantity_tolerance = self._parse_percentage(
            contract.quantity_tolerance
        )

        for match in line_matches:
            item_code = match["item_code"]

            contract_item = match["contract"]
            purchase_order_item = match["purchase_order"]
            invoice_item = match["invoice"]

            # Contract → PO validation
            if (
                contract_item is not None
                and purchase_order_item is not None
            ):
                allowed_quantity = contract_item.quantity * (
                    1 + quantity_tolerance / 100
                )

                if purchase_order_item.quantity > allowed_quantity:
                    exceptions.append(
                        ValidationException(
                            type="QUANTITY_MISMATCH",
                            field="quantity",
                            item_code=item_code,
                            expected=allowed_quantity,
                            actual=purchase_order_item.quantity,
                            tolerance=contract.quantity_tolerance,
                            source=purchase_order_item.source,
                        )
                    )

            # PO → Invoice validation
            if (
                purchase_order_item is not None
                and invoice_item is not None
            ):
                if invoice_item.quantity > purchase_order_item.quantity:
                    exceptions.append(
                        ValidationException(
                            type="QUANTITY_MISMATCH",
                            item_code=item_code,
                            field="quantity",
                            expected=purchase_order_item.quantity,
                            actual=invoice_item.quantity,
                            tolerance=None,
                            source=invoice_item.source,
                        )
                    )

        return ValidationResult(
            status="EXCEPTION" if exceptions else "PASS",
            exceptions=exceptions,
        )

    @staticmethod
    def _parse_percentage(value: str | None) -> float:
        if not value:
            return 0.0

        value = (
            value
            .strip()
            .replace("%", "")
            .replace("±", "")
        )

        return float(value)