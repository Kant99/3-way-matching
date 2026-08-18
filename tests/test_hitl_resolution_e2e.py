from datetime import datetime, timezone
from pathlib import Path

from app.capabilities.evidence_generator import (
    EvidenceGenerator,
)
from app.capabilities.hitl_decision import (
    HITLDecisionCapability,
)
from app.capabilities.hitl_routing import (
    HITLRoutingCapability,
)
from app.matching.matching_engine import (
    MatchingEngine,
)
from app.models.contract import Contract
from app.models.hitl_case import (
    HITLCaseStatus,
)
from app.models.hitl_decision import (
    HITLDecision,
    HITLDecisionType,
)
from app.models.invoice import Invoice
from app.models.line_item import LineItem
from app.models.purchase_order import PurchaseOrder
from app.models.source_reference import (
    SourceReference,
)


INVOICE_PATH = (
    "data/invoices/invoice_INV-2026-5001.pdf"
)


def create_documents():
    """
    Create a deliberately invalid 3-way matching scenario.

    Contract:
        Quantity = 100
        Price = 250

    PO:
        Quantity = 100
        Price = 250

    Invoice:
        Quantity = 100
        Price = 260

    Expected:
        PRICE_MISMATCH
    """

    source = SourceReference(
        document_id="INV-2026-5001",
        document_path=INVOICE_PATH,
        page_number=1,
        polygon=[
            {"x": 5.1295, "y": 3.6172},
            {"x": 5.4651, "y": 3.6166},
            {"x": 5.4648, "y": 3.7228},
            {"x": 5.1297, "y": 3.7238},
        ],
    )

    contract = Contract(
        contract_id="CON-2026-001",
        contract_number="CON-2026-001",
        price_tolerance="±2%",
        quantity_tolerance="+5%",
        line_items=[
            LineItem(
                item_code="ITM-001",
                description=(
                    "Industrial Safety Gloves"
                ),
                quantity=100,
                unit="Pair",
                unit_price=250,
                tax="18%",
                amount=25000,
            )
        ],
    )

    purchase_order = PurchaseOrder(
        po_id="PO-2026-1001",
        po_number="PO-2026-1001",
        contract_reference="CON-2026-001",
        line_items=[
            LineItem(
                item_code="ITM-001",
                description=(
                    "Industrial Safety Gloves"
                ),
                quantity=100,
                unit="Pair",
                unit_price=250,
                tax="18%",
                amount=25000,
            )
        ],
    )

    invoice = Invoice(
        invoice_id="INV-2026-5001",
        invoice_number="INV-2026-5001",
        purchase_order_reference=(
            "PO-2026-1001"
        ),
        line_items=[
            LineItem(
                item_code="ITM-001",
                description=(
                    "Industrial Safety Gloves"
                ),
                quantity=100,
                unit="Pair",
                unit_price=260,
                tax="18%",
                amount=26000,
                source=source,
            )
        ],
    )

    return (
        contract,
        purchase_order,
        invoice,
    )


def test_complete_hitl_resolution_flow(
    tmp_path,
):
    # --------------------------------------------------
    # 1. Verify source document exists
    # --------------------------------------------------

    assert Path(
        INVOICE_PATH
    ).exists()

    # --------------------------------------------------
    # 2. Create documents
    # --------------------------------------------------

    (
        contract,
        purchase_order,
        invoice,
    ) = create_documents()

    # --------------------------------------------------
    # 3. Run deterministic matching
    # --------------------------------------------------

    evidence_generator = EvidenceGenerator(
        output_dir=str(
            tmp_path / "evidence"
        )
    )

    matching_engine = MatchingEngine(
        evidence_generator=evidence_generator
    )

    validation_result = (
        matching_engine.match(
            contract,
            purchase_order,
            invoice,
        )
    )

    # --------------------------------------------------
    # 4. Verify validation exception
    # --------------------------------------------------

    assert (
        validation_result.status
        == "EXCEPTION"
    )

    assert (
        len(
            validation_result.exceptions
        )
        == 1
    )

    exception = (
        validation_result.exceptions[0]
    )

    assert (
        exception.type
        == "PRICE_MISMATCH"
    )

    assert (
        exception.item_code
        == "ITM-001"
    )

    assert (
        exception.field
        == "unit_price"
    )

    # --------------------------------------------------
    # 5. Verify whole-row evidence
    # --------------------------------------------------

    assert exception.evidence

    assert (
        len(exception.evidence)
        == 1
    )

    evidence = (
        exception.evidence[0]
    )

    assert (
        evidence["field"]
        == "whole_row"
    )

    evidence_path = Path(
        evidence["snip_path"]
    )

    assert evidence_path.exists()

    # --------------------------------------------------
    # 6. Route to HITL
    # --------------------------------------------------

    routing = HITLRoutingCapability()

    hitl_case = routing.route(
        validation_result
    )

    assert hitl_case is not None

    # --------------------------------------------------
    # 7. Verify PENDING state
    # --------------------------------------------------

    assert (
        hitl_case.status
        == HITLCaseStatus.PENDING
    )

    assert (
        hitl_case.decision
        is None
    )

    assert (
        hitl_case.reviewer
        is None
    )

    # Evidence must be carried into HITL.
    assert hitl_case.evidence

    assert (
        len(hitl_case.evidence)
        == 1
    )

    assert (
        hitl_case.evidence[0]["field"]
        == "whole_row"
    )

    # --------------------------------------------------
    # 8. Human makes APPROVE decision
    # --------------------------------------------------

    decision_timestamp = (
        datetime.now(timezone.utc)
    )

    human_decision = HITLDecision(
        decision=HITLDecisionType.APPROVE,
        reviewer="reviewer-001",
        comment=(
            "Invoice reviewed and "
            "commercially approved."
        ),
        timestamp=decision_timestamp,
    )

    # --------------------------------------------------
    # 9. Apply decision
    # --------------------------------------------------

    decision_capability = (
        HITLDecisionCapability()
    )

    reviewed_case = (
        decision_capability.apply(
            hitl_case,
            human_decision,
        )
    )

    # --------------------------------------------------
    # 10. Verify REVIEWED state
    # --------------------------------------------------

    assert (
        reviewed_case.status
        == HITLCaseStatus.REVIEWED
    )

    assert (
        reviewed_case.decision
        is human_decision
    )

    assert (
        reviewed_case.reviewer
        == "reviewer-001"
    )

    assert (
        reviewed_case.decision.decision
        == HITLDecisionType.APPROVE
    )

    assert (
        reviewed_case.decision.comment
        == (
            "Invoice reviewed and "
            "commercially approved."
        )
    )

    assert (
        reviewed_case.decision.timestamp
        == decision_timestamp
    )

    # --------------------------------------------------
    # 11. Original validation must remain intact
    # --------------------------------------------------

    assert (
        reviewed_case.validation_result
        is validation_result
    )

    assert (
        reviewed_case.validation_result
        .status
        == "EXCEPTION"
    )

    assert (
        len(
            reviewed_case.validation_result
            .exceptions
        )
        == 1
    )

    assert (
        reviewed_case.validation_result
        .exceptions[0]
        .type
        == "PRICE_MISMATCH"
    )

    # --------------------------------------------------
    # 12. Evidence must remain intact
    # --------------------------------------------------

    assert (
        reviewed_case.evidence
        == hitl_case.evidence
    )

    assert (
        len(reviewed_case.evidence)
        == 1
    )

    reviewed_evidence = (
        reviewed_case.evidence[0]
    )

    assert (
        reviewed_evidence["field"]
        == "whole_row"
    )

    assert Path(
        reviewed_evidence["snip_path"]
    ).exists()

    # --------------------------------------------------
    # 13. Final output
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("HITL RESOLUTION E2E")
    print("=" * 80)

    print(
        f"Validation Status : "
        f"{validation_result.status}"
    )

    print(
        f"Exception         : "
        f"{exception.type}"
    )

    print(
        f"Item              : "
        f"{exception.item_code}"
    )

    print(
        f"Expected          : "
        f"{exception.expected}"
    )

    print(
        f"Actual            : "
        f"{exception.actual}"
    )

    print(
        f"HITL Case         : "
        f"{hitl_case.case_id}"
    )

    print(
        f"Initial Status    : "
        f"{HITLCaseStatus.PENDING.value}"
    )

    print(
        f"Decision          : "
        f"{human_decision.decision.value}"
    )

    print(
        f"Reviewer          : "
        f"{human_decision.reviewer}"
    )

    print(
        f"Final Status      : "
        f"{reviewed_case.status.value}"
    )

    print(
        f"Evidence          : "
        f"{reviewed_evidence['snip_path']}"
    )

    print("=" * 80)