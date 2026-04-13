from __future__ import annotations

import logging
import os
import threading
from typing import ClassVar, Final

from rich.console import Console

_LOG_ENV_VAR: Final[str] = "LOG_LEVEL"
_ROOT_NAME: Final[str] = "gaserp"
_lock = threading.Lock()
_configured = False


def _parse_level() -> int:
    raw = os.getenv(_LOG_ENV_VAR, "INFO")
    if raw is None or not str(raw).strip():
        return logging.INFO
    name = str(raw).strip().upper()
    return getattr(logging, name, logging.INFO)


class _LevelColoredRichHandler(logging.Handler):
    """One Rich color per line from log level only (no syntax highlighting per segment)."""

    _STYLES: ClassVar[dict[int, str]] = {
        logging.DEBUG: "dim",
        logging.INFO: "green",
        logging.WARNING: "yellow",
        logging.ERROR: "red",
        logging.CRITICAL: "bold red",
    }

    def __init__(self, level: int = logging.NOTSET) -> None:
        super().__init__(level)
        self._console = Console(stderr=True, highlight=False, soft_wrap=True)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            text = self.format(record)
            style = self._STYLES.get(record.levelno, "white")
            self._console.print(text, style=style, highlight=False, end="\n")
        except Exception:
            self.handleError(record)


def configure_logging() -> None:
    """Attach a Rich-backed handler to the ``gaserp`` logger tree. Idempotent."""
    global _configured
    with _lock:
        if _configured:
            return
        level = _parse_level()
        root = logging.getLogger(_ROOT_NAME)
        root.setLevel(level)
        root.handlers.clear()
        handler = _LevelColoredRichHandler(level=level)
        handler.setFormatter(
            logging.Formatter(
                fmt="[%(asctime)s] %(levelname)s %(message)s (%(filename)s:%(lineno)d)",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        root.addHandler(handler)
        root.propagate = False
        _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Return a child logger (e.g. pass ``__name__``).

    Levels: ``debug``, ``info``, ``warning``, ``error``, ``critical`` (stdlib ``logging`` API).
    Log level is read from the environment via ``os.getenv("LOG_LEVEL", "INFO")``.
    """
    configure_logging()
    return logging.getLogger(f"{_ROOT_NAME}.{name}")
