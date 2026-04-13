from fastapi import APIRouter, FastAPI

from utils.logger import get_logger

_log = get_logger(__name__)


class HealthController:
    def __init__(self) -> None:
        self.router = APIRouter(tags=["health"])
        self.router.add_api_route("/health", self.health, methods=["GET"])
        _log.debug("HealthController: routes registered")

    def health(self) -> dict[str, str]:
        _log.info("GET /health — status probe")
        return {"status": "ok"}

    def register(self, app: FastAPI) -> None:
        app.include_router(self.router)
        _log.info("HealthController: mounted on application")
