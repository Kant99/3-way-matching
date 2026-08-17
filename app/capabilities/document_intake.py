from pathlib import Path
from typing import Dict, List
from uuid import uuid5, NAMESPACE_URL


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".tiff",
    ".bmp",
}


DOCUMENT_TYPES = {
    "contracts": "CONTRACT",
    "purchase_orders": "PURCHASE_ORDER",
    "invoices": "INVOICE",
}


class DocumentIntake:
    """
    Discovers documents from the POC data directory
    and produces basic intake metadata.

    This capability does not perform document extraction.
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)

    def discover_documents(self) -> Dict[str, List[Dict[str, object]]]:
        """
        Discover supported documents and return intake metadata.
        """

        result: Dict[str, List[Dict[str, object]]] = {
            "contracts": [],
            "purchase_orders": [],
            "invoices": [],
        }

        for folder_name, document_type in DOCUMENT_TYPES.items():

            directory = self.data_dir / folder_name

            if not directory.exists():
                continue

            for file_path in sorted(directory.iterdir()):

                if not file_path.is_file():
                    continue

                if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                    continue

                document_id = str(
                    uuid5(
                        NAMESPACE_URL,
                        str(file_path.resolve()),
                    )
                )

                result[folder_name].append(
                    {
                        "document_id": document_id,
                        "filename": file_path.name,
                        "path": str(file_path),
                        "document_type": document_type,
                        "file_extension": file_path.suffix.lower(),
                        "file_size": file_path.stat().st_size,
                    }
                )

        return result

    def classify_document(self, document_category: str) -> str:
        """
        Classify a document based on the POC data-folder category.
        """

        if document_category not in DOCUMENT_TYPES:
            raise ValueError(
                f"Unsupported document category: {document_category}"
            )

        return DOCUMENT_TYPES[document_category]