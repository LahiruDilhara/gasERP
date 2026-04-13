"""Liveness / health routes for the API."""

from fastapi import APIRouter

from utils.logger import get_logger


def _get_logger():
    return get_logger(__name__)


router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    _get_logger().info("GET /health — status probe")
    return {"status": "ok"}
