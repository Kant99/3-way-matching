┌──────────────────────────────────────────────────────────────┐
│                    INPUT DOCUMENTS                          │
│                                                              │
│       Contract PDF     PO PDF      Invoice PDF              │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                     DOCUMENT INTAKE                          │
│                                                              │
│  • Discover documents                                        │
│  • Identify document types                                   │
│  • Track document metadata                                   │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                  DOCUMENT EXTRACTION                         │
│                                                              │
│              Azure Document Intelligence                     │
│                                                              │
│  ContractExtractor     POExtractor     InvoiceExtractor      │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    CANONICALIZATION                          │
│                                                              │
│  Extracted structures → Standard domain models               │
│                                                              │
│  Contract | PurchaseOrder | Invoice | LineItem                │
│                                                              │
│                  + SourceReference                            │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                 DETERMINISTIC MATCHING ENGINE                │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │ Relationship   │  │   Quantity     │  │     Price      │ │
│  │   Validator    │  │   Validator    │  │   Validator    │ │
│  └────────────────┘  └────────────────┘  └────────────────┘ │
│                                                              │
│              Contract ↔ PO ↔ Invoice                         │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    VALIDATION RESULT                         │
│                                                              │
│                    PASS / EXCEPTION                          │
│                                                              │
│  Exceptions:                                                 │
│  • Quantity mismatch                                         │
│  • Price mismatch                                            │
│  • Relationship mismatch                                     │
│  • Other validation exceptions                               │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                   MAF AGENT                                  │
│                                                              │
│  • Orchestration                                             │
│  • Tool usage                                                │
│  • Result interpretation                                     │
│  • Business explanation                                      │
│  • Exception reasoning                                       │
└──────────────────────────────┬───────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
                  PASS                EXCEPTION
                    │                     │
                    ▼                     ▼
               Continue             Explanation
                                      │
                                      ▼
                                 HITL REVIEW
                                  WIP / NEXT