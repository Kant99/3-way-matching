from decimal import Decimal
from typing import Annotated, Any

from agent_framework import tool
from pydantic import BaseModel, Field

from app.matching.matching_engine import MatchingEngine
from app.models.contract import Contract
from app.models.invoice import Invoice
from app.models.line_item import LineItem
from app.models.purchase_order import PurchaseOrder
from app.models.source_reference import SourceReference
from app.capabilities.hitl_routing import HITLRoutingCapability
from app.models.validation_result import (
    ValidationException,
    ValidationResult,
)


class LineAmountResult(BaseModel):
    quantity: Decimal = Field(
        description="Quantity used in the calculation."
    )

    unit_price: Decimal = Field(
        description="Unit price used in the calculation."
    )

    amount: Decimal = Field(
        description="Calculated total line amount."
    )

    currency: str = Field(
        description="Currency of the calculated amount."
    )


@tool(
    name="calculate_line_amount",
    description=(
        "Calculate the total amount for a purchase order "
        "or invoice line item."
    ),
)
def calculate_line_amount(
    quantity: Annotated[
        Decimal,
        Field(description="The quantity of items on the line."),
    ],
    unit_price: Annotated[
        Decimal,
        Field(description="The unit price of one item."),
    ],
    currency: Annotated[
        str,
        Field(description="Currency code, for example INR or USD."),
    ] = "INR",
) -> LineAmountResult:
    """
    Deterministically calculate a line-item amount.
    """

    if quantity < 0:
        raise ValueError("Quantity cannot be negative.")

    if unit_price < 0:
        raise ValueError("Unit price cannot be negative.")

    amount = quantity * unit_price

    return LineAmountResult(
        quantity=quantity,
        unit_price=unit_price,
        amount=amount,
        currency=currency,
    )


def _build_line_items(
    line_items: list[dict[str, Any]],
) -> list[LineItem]:
    return [
        LineItem(
            item_code=item.get("item_code"),
            description=item.get("description"),
            quantity=item.get("quantity"),
            unit=item.get("unit"),
            unit_price=item.get("unit_price"),
            tax=item.get("tax"),
            amount=item.get("amount"),
        )
        for item in line_items
    ]


@tool(
    name="run_3_way_matching",
    description=(
        "Run deterministic 3-way matching between a contract, "
        "purchase order, and invoice. Use this tool to determine "
        "validation status and exceptions. Do not perform "
        "independent financial validation."
    ),
)
def run_3_way_matching(
    contract: Annotated[
        dict[str, Any],
        Field(description="Contract data including line items."),
    ],
    purchase_order: Annotated[
        dict[str, Any],
        Field(description="Purchase order data including line items."),
    ],
    invoice: Annotated[
        dict[str, Any],
        Field(description="Invoice data including line items."),
    ],
) -> dict[str, Any]:
    """
    Execute the existing deterministic MatchingEngine.

    This function is an adapter between the MAF agent tool
    interface and the existing canonical matching models.
    """

    contract_model = Contract(
        contract_id=contract["contract_id"],
        contract_number=contract.get("contract_number"),
        contract_date=contract.get("contract_date"),
        buyer=contract.get("buyer"),
        supplier=contract.get("supplier"),
        contract_validity=contract.get("contract_validity"),
        payment_terms=contract.get("payment_terms"),
        quantity_tolerance=contract.get("quantity_tolerance"),
        price_tolerance=contract.get("price_tolerance"),
        invoice_rule=contract.get("invoice_rule"),
        line_items=_build_line_items(
            contract.get("line_items", [])
        ),
    )

    purchase_order_model = PurchaseOrder(
        po_id=purchase_order["po_id"],
        po_number=purchase_order.get("po_number"),
        contract_reference=purchase_order.get(
            "contract_reference"
        ),
        po_date=purchase_order.get("po_date"),
        buyer=purchase_order.get("buyer"),
        supplier=purchase_order.get("supplier"),
        line_items=_build_line_items(
            purchase_order.get("line_items", [])
        ),
    )

    invoice_model = Invoice(
        invoice_id=invoice["invoice_id"],
        invoice_number=invoice.get("invoice_number"),
        purchase_order_reference=invoice.get(
            "purchase_order_reference"
        ),
        invoice_date=invoice.get("invoice_date"),
        due_date=invoice.get("due_date"),
        vendor=invoice.get("vendor"),
        customer=invoice.get("customer"),
        subtotal=invoice.get("subtotal"),
        total_tax=invoice.get("total_tax"),
        total=invoice.get("total"),
        line_items=_build_line_items(
            invoice.get("line_items", [])
        ),
    )

    engine = MatchingEngine()

    result = engine.match(
        contract_model,
        purchase_order_model,
        invoice_model,
    )

    return {
        "status": result.status,
        "exceptions": [
            {
                "type": exception.type,
                "item_code": exception.item_code,
                "field": exception.field,
                "expected": exception.expected,
                "actual": exception.actual,
                "tolerance": exception.tolerance,
                "source": (
                    {
                        "document_id": exception.source.document_id,
                        "document_path": exception.source.document_path,
                        "page_number": exception.source.page_number,
                        "polygon": exception.source.polygon,
                    }
                    if exception.source
                    else None
                ),
                "evidence": exception.evidence,
            }
            for exception in result.exceptions
        ],
    }

@tool(
    name="route_to_hitl",
    description=(
        "Route a deterministic validation exception to a human "
        "reviewer. Use this tool only when the validation result "
        "has status EXCEPTION. This tool creates a pending HITL "
        "case and does not approve, reject, or override the "
        "financial validation result."
    ),
)
def route_to_hitl(
    validation_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert a deterministic validation result into a HITL case.

    This is an adapter between the MAF agent tool interface and
    the deterministic HITLRoutingCapability.
    """

    exceptions = []

    for exception in validation_result.get("exceptions", []):
        source_data = exception.get("source")

        source = None

        if source_data:
            source = SourceReference(
                document_id=source_data.get("document_id"),
                document_path=source_data.get("document_path"),
                page_number=source_data.get("page_number"),
                polygon=source_data.get("polygon"),
            )

        exceptions.append(
            ValidationException(
                type=exception.get("type"),
                item_code=exception.get("item_code"),
                field=exception.get("field"),
                expected=exception.get("expected"),
                actual=exception.get("actual"),
                tolerance=exception.get("tolerance"),
                source=source,
                evidence=exception.get("evidence", []),
            )
        )

    result = ValidationResult(
        status=validation_result.get("status"),
        exceptions=exceptions,
    )

    router = HITLRoutingCapability()

    hitl_case = router.route(result)

    if hitl_case is None:
        return {
            "status": "NO_HITL_REQUIRED",
            "case": None,
        }

    return {
        "status": "HITL_REQUIRED",
        "case": {
            "case_id": hitl_case.case_id,
            "status": hitl_case.status.value,
            "created_at": hitl_case.created_at.isoformat(),
            "reviewer": hitl_case.reviewer,
            "validation_result": {
                "status": hitl_case.validation_result.status,
                "exceptions": [
                    {
                        "type": exception.type,
                        "item_code": exception.item_code,
                        "field": exception.field,
                        "expected": exception.expected,
                        "actual": exception.actual,
                        "tolerance": exception.tolerance,
                        "source": (
                            {
                                "document_id": (
                                    exception.source.document_id
                                ),
                                "document_path": (
                                    exception.source.document_path
                                ),
                                "page_number": (
                                    exception.source.page_number
                                ),
                                "polygon": exception.source.polygon,
                            }
                            if exception.source
                            else None
                        ),
                        "evidence": exception.evidence,
                    }
                    for exception
                    in hitl_case.validation_result.exceptions
                ],
            },
        },
    }