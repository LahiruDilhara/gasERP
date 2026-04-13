from abc import abstractmethod

from sqlalchemy.orm import Session

from interfaces.IDBConnection import IDBConnection


class IDBMSConnection(IDBConnection):
    @abstractmethod
    def get_session(self) -> Session:
        """Return a new SQLAlchemy session; caller is responsible for closing it."""
