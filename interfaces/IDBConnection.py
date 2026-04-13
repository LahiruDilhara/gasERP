from abc import ABC, abstractmethod


class IDBConnection(ABC):
    @abstractmethod
    def validateConnection(self) -> None:
        """Verify that the database connection is usable."""
