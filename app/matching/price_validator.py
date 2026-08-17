from app.models.contract import Contract
from app.models.purchase_order import PurchaseOrder
from app.models.invoice import Invoice
from app.models.validation_result import (
    ValidationException,
    ValidationResult,
)


class PriceValidator:
    def validate(
        self,
        contract: Contract,
        purchase_order: PurchaseOrder,
        invoice: Invoice,
        line_matches: list[dict],
    ) -> ValidationResult:
        exceptions = []

        price_tolerance = self._parse_percentage(
            contract.price_tolerance
        )

        for match in line_matches:
            item_code = match["item_code"]

            contract_item = match["contract"]
            purchase_order_item = match["purchase_order"]
            invoice_item = match["invoice"]

            # Contract → PO price validation
            if (
                contract_item is not None
                and purchase_order_item is not None
            ):
                minimum_price = contract_item.unit_price * (
                    1 - price_tolerance / 100
                )

                maximum_price = contract_item.unit_price * (
                    1 + price_tolerance / 100
                )

                if not (
                    minimum_price
                    <= purchase_order_item.unit_price
                    <= maximum_price
                ):
                    exceptions.append(
                        ValidationException(
                            type="PRICE_MISMATCH",
                            field="unit_price",
                            item_code=item_code,
                            expected={
                                "min": minimum_price,
                                "max": maximum_price,
                            },
                            actual=purchase_order_item.unit_price,
                            tolerance=contract.price_tolerance,
                            source=purchase_order_item.source,
                        )
                    )

            # PO → Invoice price validation
            if (
                purchase_order_item is not None
                and invoice_item is not None
            ):
                if (
                    invoice_item.unit_price
                    > purchase_order_item.unit_price
                ):
                    exceptions.append(
                        ValidationException(
                            type="PRICE_MISMATCH",
                            item_code=item_code,
                            field="unit_price",
                            expected=purchase_order_item.unit_price,
                            actual=invoice_item.unit_price,
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