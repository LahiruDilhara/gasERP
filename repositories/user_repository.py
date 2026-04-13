from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from db.postgresql import PostgreSQLConnection
from models.user import User


class UserRepository:
    def __init__(self, connection: PostgreSQLConnection) -> None:
        self._connection = connection

    def username_exists(self, username: str) -> bool:
        session = self._connection.get_session()
        try:
            stmt = select(User.id).where(User.username == username).limit(1)
            return session.execute(stmt).scalar_one_or_none() is not None
        finally:
            session.close()

    def find_active_by_id(self, user_id: uuid.UUID) -> User | None:
        session = self._connection.get_session()
        try:
            stmt = select(User).where(
                User.id == user_id,
                User.is_deleted.is_(False),
                User.is_active.is_(True),
            )
            user = session.execute(stmt).scalar_one_or_none()
            if user is not None:
                session.expunge(user)
            return user
        finally:
            session.close()

    def find_active_by_username(self, username: str) -> User | None:
        session = self._connection.get_session()
        try:
            stmt = select(User).where(
                User.username == username,
                User.is_deleted.is_(False),
            )
            user = session.execute(stmt).scalar_one_or_none()
            if user is not None:
                session.expunge(user)
            return user
        finally:
            session.close()

    def create(
        self,
        *,
        user_id: uuid.UUID,
        username: str,
        password_hash: str,
        role: str,
    ) -> User:
        session = self._connection.get_session()
        try:
            user = User(
                id=user_id,
                username=username,
                password_hash=password_hash,
                role=role,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            session.expunge(user)
            return user
        except IntegrityError:
            session.rollback()
            raise
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
