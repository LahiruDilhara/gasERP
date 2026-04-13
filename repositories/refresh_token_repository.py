from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from db.postgresql import PostgreSQLConnection
from models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, connection: PostgreSQLConnection) -> None:
        self._connection = connection

    def create(
        self,
        *,
        token_id: uuid.UUID,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> None:
        session = self._connection.get_session()
        try:
            row = RefreshToken(
                id=token_id,
                user_id=user_id,
                token_hash=token_hash,
                expires_at=expires_at,
            )
            session.add(row)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def find_valid_by_hash(self, token_hash: str) -> RefreshToken | None:
        session = self._connection.get_session()
        try:
            now = datetime.now(timezone.utc)
            stmt = select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.expires_at > now,
                RefreshToken.revoked_at.is_(None),
            )
            row = session.execute(stmt).scalar_one_or_none()
            if row is not None:
                session.expunge(row)
            return row
        finally:
            session.close()
