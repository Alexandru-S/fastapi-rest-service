from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from models.hotel import HotelAction


class HotelCreate(BaseModel):
    name: str
    location_id: int


class HotelRead(BaseModel):
    id: UUID
    name: str
    location_id: int
    created_at: datetime
    updated_at: datetime | None
    deleted_at: datetime | None
    action: HotelAction

    model_config = ConfigDict(from_attributes=True)
