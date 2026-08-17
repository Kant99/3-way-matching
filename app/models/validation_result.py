from dataclasses import dataclass, field as dataclass_field
from typing import Any, List, Optional

from app.models.source_reference import SourceReference


@dataclass
class ValidationException:
    type: str
    item_code: Optional[str] = None
    field: Optional[str] = None
    expected: Any = None
    actual: Any = None
    tolerance: Optional[str] = None
    source: Optional[SourceReference] = None
    evidence: List[dict] = dataclass_field(
        default_factory=list
    )


@dataclass
class ValidationResult:
    status: str
    exceptions: List[ValidationException] = dataclass_field(
        default_factory=list
    )