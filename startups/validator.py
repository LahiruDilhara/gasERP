from core.di.container import Container
from startups.dbValidator import validate as validate_database
from utils.logger import get_logger

_log = get_logger(__name__)


def run_all_validators(container: Container) -> None:
    """Execute every startup validator under ``./startups``."""
    _log.info("Validator suite: starting")
    validate_database(container)
    _log.info("Validator suite: all passed")
