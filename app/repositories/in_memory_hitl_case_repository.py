from typing import Dict, Optional

from app.models.hitl_case import HITLCase
from app.repositories.hitl_case_repository import (
    HITLCaseRepository,
)


class InMemoryHITLCaseRepository(
    HITLCaseRepository
):
    """
    In-memory implementation of the HITL case repository.

    This implementation is intended for the POC.

    Cases are stored in a Python dictionary and therefore
    are lost when the application process terminates.

    The repository interface allows this implementation to
    be replaced by a persistent database implementation
    later without changing the HITL workflow.
    """

    def __init__(self):
        self._cases: Dict[
            str,
            HITLCase,
        ] = {}

    def save(
        self,
        hitl_case: HITLCase,
    ) -> HITLCase:
        """
        Save a new HITL case.

        Raises:
            ValueError: if the case is None.
            ValueError: if a case with the same ID
                        already exists.
        """

        if hitl_case is None:
            raise ValueError(
                "HITL case cannot be None."
            )

        if hitl_case.case_id in self._cases:
            raise ValueError(
                f"HITL case already exists: "
                f"{hitl_case.case_id}"
            )

        self._cases[
            hitl_case.case_id
        ] = hitl_case

        return hitl_case

    def get(
        self,
        case_id: str,
    ) -> Optional[HITLCase]:
        """
        Retrieve an HITL case by case ID.

        Returns None when the case does not exist.
        """

        if not case_id:
            raise ValueError(
                "case_id cannot be empty."
            )

        return self._cases.get(
            case_id
        )

    def update(
        self,
        hitl_case: HITLCase,
    ) -> HITLCase:
        """
        Update an existing HITL case.

        Raises:
            ValueError: if the case is None.
            ValueError: if the case does not exist.
        """

        if hitl_case is None:
            raise ValueError(
                "HITL case cannot be None."
            )

        if (
            hitl_case.case_id
            not in self._cases
        ):
            raise ValueError(
                f"HITL case does not exist: "
                f"{hitl_case.case_id}"
            )

        self._cases[
            hitl_case.case_id
        ] = hitl_case

        return hitl_case