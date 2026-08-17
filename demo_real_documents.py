import asyncio
import json

from app.agents.matching_agent import create_matching_agent
from app.capabilities.contract_extractor import ContractExtractor
from app.capabilities.document_intake import DocumentIntake
from app.capabilities.invoice_extractor import InvoiceExtractor
from app.capabilities.purchase_order_extractor import (
    PurchaseOrderExtractor,
)
from app.canonicalization.canonicalizer import Canonicalizer
from app.matching.matching_engine import MatchingEngine


# ============================================================
# DEMO CONFIGURATION
# ============================================================

DEMO_DISCREPANCY = True


# ============================================================
# MAIN DEMO
# ============================================================

async def main():

    print("\n" + "=" * 70)
    print("AGENTIC 3-WAY MATCHING POC")
    print("=" * 70)

    # ========================================================
    # 1. DOCUMENT INTAKE
    # ========================================================

    print("\n[1] DOCUMENT INTAKE")

    intake = DocumentIntake()

    documents = intake.discover_documents()

    if not documents.get("contracts"):
        raise RuntimeError(
            "No contract document found."
        )

    if not documents.get("purchase_orders"):
        raise RuntimeError(
            "No purchase order document found."
        )

    if not documents.get("invoices"):
        raise RuntimeError(
            "No invoice document found."
        )

    contract_doc = documents["contracts"][0]
    po_doc = documents["purchase_orders"][0]
    invoice_doc = documents["invoices"][0]

    print(
        f"Contract : {contract_doc['filename']}"
    )

    print(
        f"PO       : {po_doc['filename']}"
    )

    print(
        f"Invoice  : {invoice_doc['filename']}"
    )

    # ========================================================
    # 2. DOCUMENT EXTRACTION
    # ========================================================

    print("\n[2] DOCUMENT EXTRACTION")

    contract_extractor = ContractExtractor()
    po_extractor = PurchaseOrderExtractor()
    invoice_extractor = InvoiceExtractor()

    contract_data = (
        contract_extractor.extract_contract(
            contract_doc["path"]
        )
    )

    po_data = (
        po_extractor.extract_purchase_order(
            po_doc["path"]
        )
    )

    invoice_data = (
        invoice_extractor.extract_invoice(
            invoice_doc["path"]
        )
    )

    print(
        "Contract extracted:",
        contract_data["contract_number"]["value"],
    )

    print(
        "PO extracted:",
        po_data["po_number"]["value"],
    )

    print(
        "Invoice extracted:",
        invoice_data["invoice_number"]["value"],
    )

    # ========================================================
    # 3. CANONICALIZATION
    # ========================================================

    print("\n[3] CANONICALIZATION")

    canonicalizer = Canonicalizer()

    contract = canonicalizer.canonicalize_contract(
        contract_data,
        document_id=contract_doc["document_id"],
    )

    purchase_order = (
        canonicalizer.canonicalize_purchase_order(
            po_data,
            document_id=po_doc["document_id"],
        )
    )

    invoice = canonicalizer.canonicalize_invoice(
        invoice_data,
        document_id=invoice_doc["document_id"],
    )

    print(
        "Contract model :",
        contract.contract_number,
    )

    print(
        "PO model       :",
        purchase_order.po_number,
    )

    print(
        "Invoice model  :",
        invoice.invoice_number,
    )

    print(
        "Contract lines :",
        len(contract.line_items),
    )

    print(
        "PO lines       :",
        len(purchase_order.line_items),
    )

    print(
        "Invoice lines  :",
        len(invoice.line_items),
    )

    # ========================================================
    # 4. SHOW EXTRACTED/CANONICAL DATA
    # ========================================================

    print("\n[4] CANONICAL LINE ITEMS")

    print("\nContract:")

    for line in contract.line_items:
        print(
            f"  {line.item_code} | "
            f"{line.description} | "
            f"Qty={line.quantity} | "
            f"Price={line.unit_price}"
        )

    print("\nPurchase Order:")

    for line in purchase_order.line_items:
        print(
            f"  {line.item_code} | "
            f"{line.description} | "
            f"Qty={line.quantity} | "
            f"Price={line.unit_price}"
        )

    print("\nInvoice:")

    for line in invoice.line_items:
        print(
            f"  {line.item_code} | "
            f"{line.description} | "
            f"Qty={line.quantity} | "
            f"Price={line.unit_price}"
        )

    # ========================================================
    # 5. CONTROLLED DEMO DISCREPANCY
    # ========================================================

    if DEMO_DISCREPANCY:

        print(
            "\n[DEMO] Injecting controlled "
            "invoice discrepancy"
        )

        if not invoice.line_items:
            raise RuntimeError(
                "Invoice contains no line items."
            )

        original_quantity = (
            invoice.line_items[0].quantity
        )

        original_price = (
            invoice.line_items[0].unit_price
        )

        invoice.line_items[0].quantity = 110
        invoice.line_items[0].unit_price = 260

        print(
            f"Invoice {invoice.line_items[0].item_code} "
            "modified for demonstration:"
        )

        print(
            f"Quantity: {original_quantity} -> "
            f"{invoice.line_items[0].quantity}"
        )

        print(
            f"Unit Price: {original_price} -> "
            f"{invoice.line_items[0].unit_price}"
        )

        print(
            "\nNOTE: This is a controlled demo discrepancy. "
            "The source documents remain unchanged."
        )

    # ========================================================
    # 6. DETERMINISTIC MATCHING
    # ========================================================

    print(
        "\n[5] DETERMINISTIC MATCHING"
    )

    engine = MatchingEngine()

    deterministic_result = engine.match(
        contract,
        purchase_order,
        invoice,
    )

    print(
        "\nDeterministic Matching Status:",
        deterministic_result.status,
    )

    # ========================================================
    # 7. DISPLAY DETERMINISTIC EXCEPTIONS
    # ========================================================

    print("\nDeterministic Exceptions:")

    if not deterministic_result.exceptions:

        print(
            "  No exceptions found."
        )

    else:

        for exception in (
            deterministic_result.exceptions
        ):

            print(
                f"\n  Type     : {exception.type}"
            )

            print(
                f"  Field    : {exception.field}"
            )

            print(
                f"  Expected : {exception.expected}"
            )

            print(
                f"  Actual   : {exception.actual}"
            )

            if getattr(
                exception,
                "tolerance",
                None,
            ) is not None:

                print(
                    f"  Tolerance: "
                    f"{exception.tolerance}"
                )

    # ========================================================
    # 8. PREPARE DETERMINISTIC RESULT FOR AGENT
    # ========================================================

    print(
        "\n[6] PREPARING RESULT FOR MAF AGENT"
    )

    deterministic_result_for_agent = {
        "status": str(
            deterministic_result.status
        ),
        "exceptions": [],
    }

    for exception in (
        deterministic_result.exceptions
    ):

        exception_data = {
            "type": str(exception.type),
            "field": str(exception.field),
            "expected": exception.expected,
            "actual": exception.actual,
        }

        tolerance = getattr(
            exception,
            "tolerance",
            None,
        )

        if tolerance is not None:
            exception_data["tolerance"] = tolerance

        deterministic_result_for_agent[
            "exceptions"
        ].append(exception_data)

    print(
        json.dumps(
            deterministic_result_for_agent,
            indent=2,
            default=str,
        )
    )

    # ========================================================
    # 9. START MAF AGENT
    # ========================================================

    print(
        "\n[7] STARTING MAF AGENT"
    )

    agent = create_matching_agent()

    # ========================================================
    # 10. AGENT EXPLANATION
    # ========================================================

    prompt = f"""
You are the orchestration and explanation agent for
a contract, purchase order, and invoice 3-way matching
workflow.

The deterministic matching engine has already executed.

IMPORTANT:

The deterministic result below is authoritative.

Do NOT recalculate the values.

Do NOT change the status.

Do NOT invent additional exceptions.

Do NOT claim that the documents passed if the status
is EXCEPTION.

Your job is to explain the deterministic result to
a business user.

Deterministic Matching Result:

{json.dumps(
    deterministic_result_for_agent,
    indent=2,
    default=str,
)}

Provide your response using this structure:

OVERALL STATUS:
State PASS or EXCEPTION.

EXCEPTIONS:
List every exception returned by the deterministic
matching engine.

DETAILS:
For every exception explain:
- Exception type
- Field
- Expected value
- Actual value
- Tolerance, if available

BUSINESS IMPACT:
Explain what the discrepancy means for the
Contract, Purchase Order, and Invoice.

RECOMMENDED ACTION:
If the status is EXCEPTION, state that the case
should be reviewed by a human.

HITL STATUS:
State exactly:

"HITL routing is currently work in progress."

Do not claim that a HITL workflow has been triggered.
"""

    print(
        "\n[8] RUNNING MAF AGENT EXPLANATION"
    )

    response = await agent.run(prompt)

    # ========================================================
    # 11. FINAL RESULT
    # ========================================================

    print("\n" + "=" * 70)
    print("FINAL AGENT RESULT")
    print("=" * 70)

    print(response.text)

    print("=" * 70)

    # ========================================================
    # 12. DEMO SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("DEMO FLOW COMPLETED")
    print("=" * 70)

    print(
        "Real documents       : PASS"
    )

    print(
        "Document extraction   : PASS"
    )

    print(
        "Canonicalization      : PASS"
    )

    print(
        "Deterministic matching:",
        deterministic_result.status,
    )

    print(
        "Agent explanation      : PASS"
    )

    print(
        "HITL routing          : WORK IN PROGRESS"
    )

    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())