from pydantic import Field

from dto.token_response_dto import TokenResponseDto


class LoginTokenResponseDto(TokenResponseDto):
    """Login response: includes opaque refresh token (stored hashed in DB)."""

    refresh_token: str = Field(..., min_length=10)
