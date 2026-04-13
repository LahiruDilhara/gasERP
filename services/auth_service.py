from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError

from config.applicationConfig import ApplicationSettings
from db.postgresql import PostgreSQLConnection
from dto.login_dto import LoginDto
from dto.login_token_response_dto import LoginTokenResponseDto
from dto.refresh_token_request_dto import RefreshTokenRequestDto
from dto.signup_dto import SignupDto
from dto.token_response_dto import TokenResponseDto
from dto.user_public_dto import UserPublicDto
from repositories.refresh_token_repository import RefreshTokenRepository
from repositories.user_repository import UserRepository
from utils import security


class AuthService:
    def __init__(
        self,
        connection: PostgreSQLConnection,
        settings: ApplicationSettings,
    ) -> None:
        self._settings = settings
        self._users = UserRepository(connection)
        self._refresh_tokens = RefreshTokenRepository(connection)

    def _to_public(self, user) -> UserPublicDto:
        return UserPublicDto.model_validate(user)

    def _issue_access_token(self, user) -> tuple[str, int]:
        secret = self._settings.jwt_secret.get_secret_value()
        return security.create_access_token(
            subject_user_id=str(user.id),
            username=user.username,
            role=user.role,
            secret=secret,
            algorithm=self._settings.jwt_algorithm,
            expire_seconds=self._settings.jwt_access_expire_seconds,
        )

    def signup(self, data: SignupDto) -> UserPublicDto:
        if self._users.username_exists(data.username):
            raise ValueError("Username already taken")

        pwd_hash = security.hash_password(data.password)
        user_id = uuid.uuid4()
        try:
            user = self._users.create(
                user_id=user_id,
                username=data.username,
                password_hash=pwd_hash,
                role=data.role,
            )
        except IntegrityError:
            raise ValueError("Username already taken") from None

        return self._to_public(user)

    def login(self, data: LoginDto) -> LoginTokenResponseDto:
        user = self._users.find_active_by_username(data.username)
        if user is None or not user.is_active:
            raise ValueError("Invalid username or password")
        if not security.verify_password(data.password, user.password_hash):
            raise ValueError("Invalid username or password")

        access_token, expires_in = self._issue_access_token(user)

        refresh_plain = secrets.token_urlsafe(48)
        refresh_hash = security.hash_refresh_token(refresh_plain)
        now = datetime.now(timezone.utc)
        refresh_expires = now + timedelta(
            seconds=self._settings.jwt_refresh_expire_seconds,
        )
        self._refresh_tokens.create(
            token_id=uuid.uuid4(),
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=refresh_expires,
        )

        return LoginTokenResponseDto(
            access_token=access_token,
            expires_in=expires_in,
            username=user.username,
            user_id=user.id,
            refresh_token=refresh_plain,
        )

    def refresh_access_token(self, data: RefreshTokenRequestDto) -> TokenResponseDto:
        token_hash = security.hash_refresh_token(data.refresh_token)
        row = self._refresh_tokens.find_valid_by_hash(token_hash)
        if row is None:
            raise ValueError("Invalid or expired refresh token")

        user = self._users.find_active_by_id(row.user_id)
        if user is None:
            raise ValueError("Invalid or expired refresh token")

        access_token, expires_in = self._issue_access_token(user)
        return TokenResponseDto(
            access_token=access_token,
            expires_in=expires_in,
            username=user.username,
            user_id=user.id,
        )
