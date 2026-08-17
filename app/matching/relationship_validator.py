from app.models.contract import Contract
from app.models.purchase_order import PurchaseOrder
from app.models.invoice import Invoice
from app.models.validation_result import (
    ValidationException,
    ValidationResult,
)


class RelationshipValidator:
    def validate(
        self,
        contract: Contract,
        purchase_order: PurchaseOrder,
        invoice: Invoice,
    ) -> ValidationResult:
        exceptions = []

        # PO → Contract
        if (
            purchase_order.contract_reference
            != contract.contract_number
        ):
            exceptions.append(
                ValidationException(
                    type="CONTRACT_REFERENCE_MISMATCH",
                    field="contract_reference",
                    expected=contract.contract_number,
                    actual=purchase_order.contract_reference,
                    source=purchase_order.source,
                )
            )

        # Invoice → PO
        if (
            invoice.purchase_order_reference
            != purchase_order.po_number
        ):
            exceptions.append(
                ValidationException(
                    type="PO_REFERENCE_MISMATCH",
                    field="purchase_order_reference",
                    expected=purchase_order.po_number,
                    actual=invoice.purchase_order_reference,
                    source=invoice.source,
                )
            )

        return ValidationResult(
            status="EXCEPTION" if exceptions else "PASS",
            exceptions=exceptions,
        )