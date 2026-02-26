from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GuestCreate(BaseModel):
    api_id: int
    location: str
    name: str
    image: str | None = None


class GuestRead(BaseModel):
    id: UUID
    api_id: int
    location: str
    name: str
    image: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
