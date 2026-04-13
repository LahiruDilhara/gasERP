from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from interfaces.IDBMSConnection import IDBMSConnection
from utils.logger import get_logger

_log = get_logger(__name__)


def _build_sync_sqlalchemy_url(
    *,
    database_url: str | None,
    db_host: str,
    db_port: int,
    db_name: str,
    db_user: str,
    db_password: str,
) -> str:
    url: str | None = None
    if database_url is not None:
        stripped = database_url.strip()
        if stripped:
            url = stripped

    if url:
        if url.startswith("postgres://"):
            url = "postgresql://" + url.removeprefix("postgres://")
        if url.startswith("postgresql://") and "+psycopg2" not in url.split("://", 1)[0]:
            url = "postgresql+psycopg2://" + url.removeprefix("postgresql://")
        _log.debug("PostgreSQL: connection string source=DATABASE_URL")
        return url

    pw = quote_plus(db_password)
    _log.debug(
        "PostgreSQL: connection string source=DB_* host=%s port=%s db=%s",
        db_host,
        db_port,
        db_name,
    )
    return (
        f"postgresql+psycopg2://{quote_plus(db_user)}:{pw}"
        f"@{db_host}:{db_port}/{db_name}"
    )


class PostgreSQLConnection(IDBMSConnection):
    def __init__(
        self,
        *,
        database_url: str | None,
        db_host: str,
        db_port: int,
        db_name: str,
        db_user: str,
        db_password: str,
        pool_size: int,
        max_overflow: int,
        pool_timeout: int,
        pool_recycle: int,
    ) -> None:
        self._engine: Engine = create_engine(
            _build_sync_sqlalchemy_url(
                database_url=database_url,
                db_host=db_host,
                db_port=db_port,
                db_name=db_name,
                db_user=db_user,
                db_password=db_password,
            ),
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,
        )
        self._session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
        )
        _log.info(
            "PostgreSQL engine ready host=%s port=%s db=%s pool_size=%s max_overflow=%s",
            db_host,
            db_port,
            db_name,
            pool_size,
            max_overflow,
        )

    @property
    def engine(self) -> Engine:
        return self._engine

    def validateConnection(self) -> None:
        _log.debug("PostgreSQL validateConnection: executing probe query")
        with self._engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        _log.info("PostgreSQL validateConnection: probe succeeded")

    def get_session(self) -> Session:
        return self._session_factory()
