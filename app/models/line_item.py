from dataclasses import dataclass
from typing import Optional

from app.models.source_reference import SourceReference


@dataclass
class LineItem:
    item_code: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    tax: Optional[float] = None
    amount: Optional[float] = None
    source: Optional[SourceReference] = None