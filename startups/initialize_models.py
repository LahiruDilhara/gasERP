"""Register ORM models and sync database schema (e.g. create_all for development)."""

from sqlalchemy.engine import Engine

import models  # noqa: F401 — load ``models`` package so all ORM classes attach to metadata
from models.base import Base
from utils.logger import get_logger


def _get_logger():
    return get_logger(__name__)


def initialize_models(engine: Engine) -> None:
    """
    Ensure SQLAlchemy metadata is loaded and tables exist for registered models.

    Imports model modules for side effects on ``Base.metadata``, then runs
    ``create_all`` on the given engine.
    """
    Base.metadata.create_all(bind=engine)
    _get_logger().info("Database tables ensured (SQLAlchemy create_all)")
