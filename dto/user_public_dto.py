import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserPublicDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str = Field(..., max_length=64)
    role: str = Field(..., max_length=32)
    created_at: datetime
    is_active: bool
    is_deleted: bool
