from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RoomCreate(BaseModel):
    room_no: int
    floors: int
    name: str | None = None


class RoomRead(BaseModel):
    id: UUID
    room_no: int
    floors: int
    name: str | None

    model_config = ConfigDict(from_attributes=True)
