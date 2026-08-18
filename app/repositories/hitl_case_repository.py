from abc import ABC, abstractmethod
from typing import Optional

from app.models.hitl_case import HITLCase


class HITLCaseRepository(ABC):
    """
    Abstract repository for HITL cases.

    The POC starts with an in-memory implementation,
    but the abstraction allows us to replace it later
    with PostgreSQL, MongoDB, Cosmos DB, etc. without
    changing the HITL workflow.
    """

    @abstractmethod
    def save(
        self,
        hitl_case: HITLCase,
    ) -> HITLCase:
        """
        Persist a new HITL case.
        """
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        case_id: str,
    ) -> Optional[HITLCase]:
        """
        Retrieve a HITL case by case ID.
        """
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        hitl_case: HITLCase,
    ) -> HITLCase:
        """
        Update an existing HITL case.
        """
        raise NotImplementedError