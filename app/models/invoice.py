from dataclasses import dataclass, field
from typing import List, Optional

from app.models.line_item import LineItem
from app.models.source_reference import SourceReference


@dataclass
class Invoice:
    invoice_id: str
    invoice_number: Optional[str] = None
    purchase_order_reference: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    vendor: Optional[str] = None
    customer: Optional[str] = None
    subtotal: Optional[float] = None
    total_tax: Optional[float] = None
    total: Optional[float] = None
    line_items: List[LineItem] = field(
        default_factory=list
    )
    source: Optional[SourceReference] = None