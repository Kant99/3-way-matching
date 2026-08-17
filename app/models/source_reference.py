from dataclasses import dataclass
from typing import Dict, List


@dataclass
class SourceReference:
    """
    Location of an extracted value in the original document.
    """

    document_id: str
    document_path: str
    page_number: int
    polygon: List[Dict[str, float]]