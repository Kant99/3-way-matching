from datetime import datetime, timezone
from pathlib import Path

from app.capabilities.evidence_generator import (
    EvidenceGenerator,
)
from app.capabilities.hitl_case_service import (
    HITLCaseService,
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
from app.repositories.in_memory_hitl_case_repository import (
    InMemoryHITLCaseRepository,
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

    Purchase Order:
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


def test_complete_persisted_hitl_flow(
    tmp_path,
):
    # ==================================================
    # 1. Verify document
    # ==================================================

    invoice_path = Path(
        INVOICE_PATH
    )

    assert invoice_path.exists()

    # ==================================================
    # 2. Create source documents
    # ==================================================

    (
        contract,
        purchase_order,
        invoice,
    ) = create_documents()

    # ==================================================
    # 3. Create deterministic matching engine
    # ==================================================

    evidence_generator = EvidenceGenerator(
        output_dir=str(
            tmp_path / "evidence"
        )
    )

    matching_engine = MatchingEngine(
        evidence_generator=evidence_generator
    )

    # ==================================================
    # 4. Execute 3-way matching
    # ==================================================

    validation_result = (
        matching_engine.match(
            contract,
            purchase_order,
            invoice,
        )
    )

    # ==================================================
    # 5. Verify deterministic exception
    # ==================================================

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

    assert (
        exception.expected
        == 250
    )

    assert (
        exception.actual
        == 260
    )

    # ==================================================
    # 6. Verify whole-row evidence
    # ==================================================

    assert exception.evidence

    assert (
        len(exception.evidence)
        == 1
    )

    exception_evidence = (
        exception.evidence[0]
    )

    assert (
        exception_evidence["field"]
        == "whole_row"
    )

    evidence_path = Path(
        exception_evidence["snip_path"]
    )

    assert evidence_path.exists()

    # ==================================================
    # 7. Create HITL persistence layer
    # ==================================================

    repository = (
        InMemoryHITLCaseRepository()
    )

    hitl_service = HITLCaseService(
        repository=repository,
        routing_capability=(
            HITLRoutingCapability()
        ),
        decision_capability=(
            HITLDecisionCapability()
        ),
    )

    # ==================================================
    # 8. Create and persist HITL case
    # ==================================================

    hitl_case = (
        hitl_service.create_case(
            validation_result
        )
    )

    assert hitl_case is not None

    assert (
        hitl_case.status
        == HITLCaseStatus.PENDING
    )

    assert (
        hitl_case.case_id
        != ""
    )

    # ==================================================
    # 9. Verify persisted PENDING case
    # ==================================================

    persisted_pending_case = (
        hitl_service.get_case(
            hitl_case.case_id
        )
    )

    assert (
        persisted_pending_case is not None
    )

    assert (
        persisted_pending_case.status
        == HITLCaseStatus.PENDING
    )

    assert (
        persisted_pending_case.decision
        is None
    )

    assert (
        persisted_pending_case.reviewer
        is None
    )

    # ==================================================
    # 10. Verify evidence survived persistence
    # ==================================================

    assert (
        persisted_pending_case.evidence
    )

    assert (
        len(
            persisted_pending_case.evidence
        )
        == 1
    )

    persisted_evidence = (
        persisted_pending_case.evidence[0]
    )

    assert (
        persisted_evidence["field"]
        == "whole_row"
    )

    assert Path(
        persisted_evidence["snip_path"]
    ).exists()

    # ==================================================
    # 11. Human review
    # ==================================================

    decision_timestamp = (
        datetime.now(timezone.utc)
    )

    decision = HITLDecision(
        decision=HITLDecisionType.APPROVE,
        reviewer="reviewer-001",
        comment=(
            "Invoice reviewed and "
            "commercially approved."
        ),
        timestamp=decision_timestamp,
    )

    # ==================================================
    # 12. Apply human decision
    # ==================================================

    reviewed_case = (
        hitl_service.apply_decision(
            hitl_case.case_id,
            decision,
        )
    )

    # ==================================================
    # 13. Verify REVIEWED state
    # ==================================================

    assert (
        reviewed_case.status
        == HITLCaseStatus.REVIEWED
    )

    assert (
        reviewed_case.decision
        is decision
    )

    assert (
        reviewed_case.reviewer
        == "reviewer-001"
    )

    # ==================================================
    # 14. Verify decision details
    # ==================================================

    assert (
        reviewed_case.decision.decision
        == HITLDecisionType.APPROVE
    )

    assert (
        reviewed_case.decision.reviewer
        == "reviewer-001"
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

    # ==================================================
    # 15. Recover final case from repository
    # ==================================================

    recovered_case = (
        hitl_service.get_case(
            hitl_case.case_id
        )
    )

    assert recovered_case is not None

    # ==================================================
    # 16. Verify recovered status
    # ==================================================

    assert (
        recovered_case.status
        == HITLCaseStatus.REVIEWED
    )

    # ==================================================
    # 17. Verify recovered decision
    # ==================================================

    assert (
        recovered_case.decision
        is decision
    )

    assert (
        recovered_case.decision.decision
        == HITLDecisionType.APPROVE
    )

    assert (
        recovered_case.reviewer
        == "reviewer-001"
    )

    # ==================================================
    # 18. Verify original validation result
    # ==================================================

    assert (
        recovered_case.validation_result
        is validation_result
    )

    assert (
        recovered_case.validation_result.status
        == "EXCEPTION"
    )

    assert (
        len(
            recovered_case.validation_result
            .exceptions
        )
        == 1
    )

    recovered_exception = (
        recovered_case.validation_result
        .exceptions[0]
    )

    assert (
        recovered_exception.type
        == "PRICE_MISMATCH"
    )

    assert (
        recovered_exception.expected
        == 250
    )

    assert (
        recovered_exception.actual
        == 260
    )

    # ==================================================
    # 19. Verify whole-row evidence survived
    # ==================================================

    assert recovered_case.evidence

    assert (
        len(recovered_case.evidence)
        == 1
    )

    recovered_evidence = (
        recovered_case.evidence[0]
    )

    assert (
        recovered_evidence["field"]
        == "whole_row"
    )

    assert (
        recovered_evidence["page_number"]
        == 1
    )

    assert Path(
        recovered_evidence["snip_path"]
    ).exists()

    # ==================================================
    # 20. Final output
    # ==================================================

    print()
    print("=" * 80)
    print("COMPLETE PERSISTED HITL FLOW")
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
        f"{decision.decision.value}"
    )

    print(
        f"Reviewer          : "
        f"{decision.reviewer}"
    )

    print(
        f"Final Status      : "
        f"{recovered_case.status.value}"
    )

    print(
        f"Evidence          : "
        f"{recovered_evidence['snip_path']}"
    )

    print("=" * 80)