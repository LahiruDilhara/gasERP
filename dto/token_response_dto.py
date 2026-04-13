import uuid

from pydantic import BaseModel, ConfigDict, Field


class TokenResponseDto(BaseModel):
    """Access-token payload returned from refresh (and shared fields for login)."""

    model_config = ConfigDict(populate_by_name=True)

    access_token: str
    token_type: str = Field(default="bearer")
    expires_in: int = Field(..., description="Access token lifetime in seconds")
    username: str
    user_id: uuid.UUID = Field(serialization_alias="userId")
