from typing import Literal

from pydantic import BaseModel, Field

RoleLiteral = Literal["user", "admin"]


class SignupDto(BaseModel):
    username: str = Field(..., min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=8, max_length=72)
    role: RoleLiteral
