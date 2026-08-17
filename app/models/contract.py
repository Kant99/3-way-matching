from dataclasses import dataclass, field
from typing import List, Optional

from app.models.line_item import LineItem
from app.models.source_reference import SourceReference


@dataclass
class Contract:
    contract_id: str
    contract_number: Optional[str] = None
    contract_date: Optional[str] = None
    buyer: Optional[str] = None
    supplier: Optional[str] = None
    contract_validity: Optional[str] = None
    payment_terms: Optional[str] = None
    quantity_tolerance: Optional[str] = None
    price_tolerance: Optional[str] = None
    invoice_rule: Optional[str] = None
    line_items: List[LineItem] = field(
        default_factory=list
    )
    source: Optional[SourceReference] = None