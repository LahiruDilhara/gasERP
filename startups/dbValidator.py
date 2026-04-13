from core.di.container import Container
from interfaces.IDBConnection import IDBConnection
from utils.logger import get_logger

_log = get_logger(__name__)


def validate(container: Container) -> None:
    """Run database connectivity checks using wired ``./db`` connection objects."""
    _log.debug("Database validator: resolving connection from container")
    connection: IDBConnection = container.db_connection()
    _log.info("Database validator: checking connectivity (validateConnection)")
    connection.validateConnection()
    _log.info("Database validator: connection OK")
