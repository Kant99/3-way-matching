# Agentic 3-Way Matching POC

An Agentic AI proof-of-concept for **Contract → Purchase Order → Invoice (3-Way Matching)** with deterministic validation, document evidence, whole-row visual evidence, Human-in-the-Loop (HITL) review, case persistence, and Microsoft Agent Framework (MAF) orchestration.

## 1. Project Overview

The POC demonstrates a workflow in which:

1. Contract, Purchase Order, and Invoice documents are ingested.
2. Document Intelligence extracts structured information and source coordinates.
3. Extracted data is converted into canonical document models.
4. Deterministic Python validators perform relationship, quantity, and price checks.
5. Validation exceptions retain source references.
6. Source coordinates are used to generate visual evidence.
7. The POC generates **whole-row evidence** for reviewer context.
8. Exceptions are routed to HITL.
9. A human reviewer can approve, reject, or override an exception.
10. HITL cases are stored through a repository abstraction.
11. MAF is used as an orchestration/explanation layer.
12. Deterministic matching remains the authoritative source of validation results.

## 2. High-Level Architecture

```text
Contract PDF ─┐
PO PDF       ─┼──> Document Intelligence
Invoice PDF  ─┘           │
                          ▼
                  Document Extraction
                          │
                          ▼
                   Canonicalization
                          │
                          ▼
              Canonical Contract / PO / Invoice
                          │
                          ▼
                 Deterministic Matching
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
 Relationship        Quantity            Price
 Validator           Validator           Validator
        └─────────────────┼─────────────────┘
                          ▼
                 ValidationResult
                    /           \
                  PASS         EXCEPTION
                   │               │
                   ▼               ▼
               Complete      SourceReference
                                   │
                                   ▼
                            EvidenceGenerator
                                   │
                                   ▼
                            Whole-Row PNG
                                   │
                                   ▼
                            HITL Routing
                                   │
                                   ▼
                         HITLCase - PENDING
                                   │
                                   ▼
                           Human Reviewer
                                   │
                         APPROVE / REJECT / OVERRIDE
                                   │
                                   ▼
                         HITLCase - REVIEWED
                                   │
                                   ▼
                         Repository / Store

MAF Agent
   │
   └── Orchestration / Explanation
       (does not override deterministic results)
```

## 3. Core Design Principle

### Deterministic matching is authoritative

The MAF agent must not independently calculate or override validation results.

The deterministic `MatchingEngine` is authoritative for:

- relationship validation
- line-item matching
- quantity validation
- price validation
- exception type
- expected value
- actual value
- tolerance

The agent is responsible for:

- orchestration
- explanation
- exception summarization
- business-friendly interpretation
- routing context

It must not invent or independently recalculate financial validation outcomes.

## 4. Current End-to-End Flow

```text
Documents
   ↓
Document Intake
   ↓
Document Extraction
   ↓
Canonicalization
   ↓
Canonical Models
   ↓
MatchingEngine
   ↓
Validation Exceptions
   ↓
SourceReference / Coordinates
   ↓
Whole-Row Evidence
   ↓
MAF Agent Explanation
   ↓
HITL Routing
   ↓
HITL Case - PENDING
   ↓
Human Review
   ↓
APPROVE / REJECT / OVERRIDE
   ↓
HITL Case - REVIEWED
   ↓
Repository
```

## 5. Major Repository Structure

```text
3waymatching/
│
├── app/
│   ├── agents/
│   │   └── matching_agent.py
│   │
│   ├── capabilities/
│   │   ├── contract_extractor.py
│   │   ├── document_intake.py
│   │   ├── evidence_generator.py
│   │   ├── hitl_case_service.py
│   │   ├── hitl_decision.py
│   │   ├── hitl_evidence.py
│   │   ├── hitl_routing.py
│   │   ├── invoice_extractor.py
│   │   ├── matching_tools.py
│   │   └── purchase_order_extractor.py
│   │
│   ├── canonicalization/
│   │   └── canonicalizer.py
│   │
│   ├── matching/
│   │   ├── matching_engine.py
│   │   ├── relationship_validator.py
│   │   ├── line_item_matcher.py
│   │   ├── quantity_validator.py
│   │   └── price_validator.py
│   │
│   ├── models/
│   │   ├── contract.py
│   │   ├── invoice.py
│   │   ├── purchase_order.py
│   │   ├── line_item.py
│   │   ├── source_reference.py
│   │   ├── validation_result.py
│   │   ├── hitl_case.py
│   │   └── hitl_decision.py
│   │
│   └── repositories/
│       ├── hitl_case_repository.py
│       └── in_memory_hitl_case_repository.py
│
├── data/
│   ├── contracts/
│   ├── purchase_orders/
│   └── invoices/
│
├── outputs/
│   └── evidence_demo/
│
├── tests/
│   └── ...
│
├── demo_full_pipeline.py
├── requirements.txt
└── README.md
```

The repository may contain additional support files and tests.

## 6. Canonical Models

The main canonical models are:

```text
Contract
PurchaseOrder
Invoice
LineItem
SourceReference
ValidationResult
ValidationException
HITLCase
HITLDecision
```

A canonical `LineItem` provides a common representation across documents:

```text
LineItem
├── item_code
├── description
├── quantity
├── unit
├── unit_price
├── tax
├── amount
└── source
```

This separates document-specific extraction from matching logic.

## 7. SourceReference and Coordinates

The POC preserves the location of extracted values in the original document.

```python
@dataclass
class SourceReference:
    document_id: str
    document_path: str
    page_number: int
    polygon: List[Dict[str, float]]
```

Example coordinate data:

```text
page_number = 1

polygon:
[
    {"x": 5.1295, "y": 3.6172},
    {"x": 5.4651, "y": 3.6166},
    {"x": 5.4648, "y": 3.7228},
    {"x": 5.1297, "y": 3.7238}
]
```

These coordinates are used to locate source values in the PDF and generate visual evidence.

## 8. Whole-Row Evidence

The POC intentionally uses **whole-row evidence** rather than showing only the individual failing field.

For example, instead of showing only:

```text
Unit Price = 275
```

the reviewer receives the complete row:

```text
ITM-001 | Industrial Safety Gloves | 110 | Pair | 275 | 30,250
```

Evidence is saved under:

```text
outputs/evidence_demo/
```

A single exception may generate an evidence image such as:

```text
invoice_INV-2026-5001_discrepancy_10pct_ITM-001_quantity_whole_row.png
```

Multiple exceptions can carry multiple evidence references.

## 9. Matching Engine

`MatchingEngine` orchestrates deterministic validation:

```text
MatchingEngine
    │
    ├── RelationshipValidator
    ├── LineItemMatcher
    ├── QuantityValidator
    ├── PriceValidator
    └── EvidenceGenerator
```

It returns:

```text
ValidationResult
├── status
└── exceptions[]
```

Each `ValidationException` can contain:

```text
ValidationException
├── type
├── item_code
├── field
├── expected
├── actual
├── tolerance
├── source
└── evidence[]
```

## 10. Example Controlled Discrepancy

For demonstration, the invoice can be modified **in memory** after extraction.

Example:

```text
Original Contract / PO:

ITM-001
Quantity   = 100
Unit Price = 250

Demo Invoice:

ITM-001
Quantity   = 110
Unit Price = 275
```

This produces:

```text
QUANTITY_MISMATCH
Expected = 100
Actual   = 110

PRICE_MISMATCH
Expected = 250
Actual   = 275
```

The source PDF is not modified by the controlled in-memory discrepancy.

## 11. MAF Agent

The MAF agent is created through:

```text
app/agents/matching_agent.py
```

It can use deterministic tools such as:

```text
calculate_line_amount
run_3_way_matching
```

The important rule is:

```text
Deterministic Matching Result
          ↓
      AUTHORITATIVE
          ↓
MAF explains/orchestrates
```

The agent should never independently change a deterministic validation result.

## 12. HITL Flow

Exceptions are routed through:

```text
ValidationResult
      ↓
HITLRoutingCapability
      ↓
HITLCase
      ↓
PENDING
```

A case contains:

```text
HITLCase
├── case_id
├── status
├── validation_result
├── created_at
├── reviewer
├── evidence
└── decision
```

## 13. Human Decision

Supported decision types:

```text
APPROVE
REJECT
OVERRIDE
```

A decision contains:

```text
HITLDecision
├── decision
├── reviewer
├── comment
└── timestamp
```

The lifecycle is:

```text
PENDING
   ↓
Human Review
   ↓
Decision
   ↓
REVIEWED
```

## 14. Manual Approval Behavior

The main demo does **not automatically approve** an exception.

When HITL is reached, the terminal waits:

```text
============================================================
HUMAN REVIEW REQUIRED
============================================================

Case ID : HITL-XXXXXXXX
Status  : PENDING

Review the generated evidence image(s).

Type APPROVED and press Enter to complete
the human review.

Reviewer input:
```

The case remains `PENDING` until the reviewer enters:

```text
APPROVED
```

Only then is the decision applied and the case changed to:

```text
REVIEWED
```

This provides an actual human-in-the-loop pause for the POC demonstration.

## 15. HITL Repository

The current POC uses:

```text
InMemoryHITLCaseRepository
```

with:

```text
save()
get()
update()
```

The repository abstraction allows a persistent database implementation to be introduced later without changing HITL business logic.

The current in-memory implementation does not survive application restarts.

## 16. Running the Main Demo

Run from the project root:

```powershell
python demo_full_pipeline.py
```

The demo flow is:

```text
[1] DOCUMENT INTAKE
      ↓
[2] DOCUMENT EXTRACTION
      ↓
[3] CANONICALIZATION
      ↓
[4] CANONICAL LINE ITEMS
      ↓
[5] DETERMINISTIC MATCHING
      ↓
[6] PREPARE RESULT FOR MAF AGENT
      ↓
[7] START MAF AGENT
      ↓
[8] MAF AGENT EXPLANATION
      ↓
[9] HITL ROUTING
      ↓
[10] HUMAN REVIEW
      ↓
WAIT FOR APPROVED
      ↓
REVIEWED
```

Generated evidence is stored in:

```text
outputs/evidence_demo/
```

Open the generated PNG files to visually inspect the invoice row that caused the exception.

## 17. Running Tests

Run the complete regression suite:

```powershell
pytest -v
```

The test suite covers the implemented areas including:

- matching
- relationship validation
- line-item matching
- quantity validation
- price validation
- source references
- evidence generation
- whole-row evidence
- HITL routing
- HITL evidence transfer
- HITL decision handling
- repository behavior
- HITL lifecycle
- persistence/recovery

## 18. Development Progress

The POC was developed incrementally:

```text
Document Extraction
        ↓
Canonical Models
        ↓
Relationship Validation
        ↓
Line Item Matching
        ↓
Quantity Validation
        ↓
Price Validation
        ↓
Source References
        ↓
Visual Evidence
        ↓
Whole-Row Evidence
        ↓
HITL Routing
        ↓
HITL Decision
        ↓
Repository Abstraction
        ↓
In-Memory Case Store
        ↓
HITL Lifecycle Service
        ↓
Persistence / Recovery
        ↓
MAF Orchestration
        ↓
Real-Document Demo
        ↓
Manual Terminal Approval
```

## 19. Current POC Status

```text
Document intake                         ✅
Document extraction                     ✅
Canonical document models               ✅
Source coordinates                      ✅
Relationship validation                 ✅
Line-item matching                      ✅
Quantity validation                     ✅
Price validation                        ✅
Validation exceptions                   ✅
Whole-row evidence                      ✅
HITL routing                            ✅
HITL case model                         ✅
HITL decision model                     ✅
HITL evidence transfer                  ✅
HITL repository abstraction             ✅
In-memory case repository               ✅
HITL lifecycle service                  ✅
Persistence/recovery tests              ✅
MAF orchestration/explanation            ✅
Real-document demo                      ✅
Manual terminal approval                ✅
Full regression suite                   ✅
```

## 20. Current Limitations

This is a POC, so several components are intentionally simplified.

### In-memory persistence

Cases are lost when the application process terminates.

### Terminal HITL

Human review is currently performed through terminal input rather than a UI.

### Controlled demo discrepancy

The demo can modify canonical invoice values in memory to reliably demonstrate exceptions.

### Evidence UI

Evidence is currently generated as PNG files rather than presented through a dedicated review interface.

### Agent scope

The MAF agent explains and orchestrates. Deterministic matching remains authoritative.

## 21. Future Production Evolution

Potential next steps:

```text
Current POC
    │
    ├── Persistent database
    ├── API boundary
    ├── HITL web UI
    ├── Authentication / authorization
    ├── Audit logging
    ├── Production document storage
    ├── Retry / failure handling
    ├── Observability
    ├── Queue-based processing
    └── Production deployment
```

These can be added without redesigning the deterministic matching engine.

## 22. Key Architectural Decisions

### Deterministic validation over LLM validation

Financial validation should be reproducible and auditable.

### Source-grounded evidence

Exceptions can point back to the original document using source coordinates.

### Whole-row evidence

The reviewer receives surrounding context rather than only an isolated field.

### Agent as orchestrator

The agent explains and coordinates rather than becoming the financial system of record.

### HITL for exceptions

Cases requiring human judgment are routed to a reviewer.

### Repository abstraction

Persistence can evolve independently from HITL business logic.

## 23. Example Final Flow

```text
Contract:
ITM-001 | Qty 100 | Price 250

PO:
ITM-001 | Qty 100 | Price 250

Invoice:
ITM-001 | Qty 110 | Price 275

        ↓

QUANTITY_MISMATCH
Expected = 100
Actual   = 110

PRICE_MISMATCH
Expected = 250
Actual   = 275

        ↓

Whole-row evidence generated

        ↓

HITL Case
Status = PENDING

        ↓

Human reviews evidence

        ↓

Reviewer enters:

APPROVED

        ↓

HITL Case
Status = REVIEWED
Decision = APPROVE
```

## 24. Quick Start

From the project root:

```powershell
# Run all tests
pytest -v

# Run the main end-to-end demonstration
python demo_full_pipeline.py
```

When the demo reaches:

```text
Reviewer input:
```

inspect the generated evidence image and enter:

```text
APPROVED
```

The case then transitions from:

```text
PENDING → REVIEWED
```

## 25. POC Objective

The POC demonstrates that a 3-way matching workflow can combine:

```text
Document Intelligence
        +
Canonical Data Modeling
        +
Deterministic Financial Validation
        +
Source-Grounded Evidence
        +
Agentic Orchestration
        +
Human-in-the-Loop
        +
Case Persistence
```

while maintaining a clear separation between:

**deterministic business correctness** and **agentic reasoning/orchestration**.
