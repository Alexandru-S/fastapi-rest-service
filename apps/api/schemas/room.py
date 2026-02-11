from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RoomCreate(BaseModel):
    room_no: int
    name: str
    floor: int


class RoomRead(BaseModel):
    id: UUID
    room_no: int
    name: str
    floor: int

    model_config = ConfigDict(from_attributes=True)
