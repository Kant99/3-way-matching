from dataclasses import dataclass, field
from typing import List, Optional

from app.models.line_item import LineItem
from app.models.source_reference import SourceReference


@dataclass
class PurchaseOrder:
    po_id: str
    po_number: Optional[str] = None
    contract_reference: Optional[str] = None
    po_date: Optional[str] = None
    buyer: Optional[str] = None
    supplier: Optional[str] = None
    line_items: List[LineItem] = field(
        default_factory=list
    )
    source: Optional[SourceReference] = None