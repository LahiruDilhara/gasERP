"""Password hashing and JWT helpers (no I/O; callers pass secrets and settings)."""

from __future__ import annotations

import hashlib
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass(frozen=True, slots=True)
class AccessTokenPayload:
    """Validated access-JWT claims (defined here so ``utils`` does not depend on ``dto``)."""

    sub: str
    user_id: str
    username: str
    role: str
    iat: int
    exp: int

    @classmethod
    def from_claims(cls, claims: Mapping[str, Any]) -> AccessTokenPayload:
        data = dict(claims)
        required = ("sub", "username", "role", "iat", "exp")
        missing = [k for k in required if k not in data or data[k] is None]
        if missing:
            raise JWTError(f"Missing JWT claim(s): {', '.join(missing)}")

        user_id_raw = data.get("userId", data.get("user_id"))
        if user_id_raw is None:
            raise JWTError("Missing JWT claim: userId")

        sub = str(data["sub"])
        user_id = str(user_id_raw)
        if sub != user_id:
            raise JWTError("Claims sub and userId must match")

        try:
            iat = int(data["iat"])
            exp = int(data["exp"])
        except (TypeError, ValueError) as exc:
            raise JWTError("Invalid iat or exp claim") from exc

        return cls(
            sub=sub,
            user_id=user_id,
            username=str(data["username"]),
            role=str(data["role"]),
            iat=iat,
            exp=exp,
        )

    def user_uuid(self) -> uuid.UUID:
        return uuid.UUID(self.user_id)


def hash_password(plain_password: str) -> str:
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return _pwd_context.verify(plain_password, password_hash)


def hash_refresh_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_access_token(
    *,
    subject_user_id: str,
    username: str,
    role: str,
    secret: str,
    algorithm: str,
    expire_seconds: int,
) -> tuple[str, int]:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(seconds=expire_seconds)
    payload: dict[str, str | int] = {
        "sub": subject_user_id,
        "userId": subject_user_id,
        "username": username,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, secret, algorithm=algorithm)
    expires_in = int((exp - now).total_seconds())
    return token, expires_in


def validate_access_token_payload(payload: Mapping[str, Any]) -> AccessTokenPayload:
    """Parse and validate raw JWT claims into a typed payload."""
    return AccessTokenPayload.from_claims(payload)


def decode_access_token(
    *,
    token: str,
    secret: str,
    algorithm: str,
) -> AccessTokenPayload:
    raw = jwt.decode(token, secret, algorithms=[algorithm])
    return validate_access_token_payload(raw)
