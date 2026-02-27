from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class TimeRange(BaseModel):
    start: datetime
    end: datetime


def _parse_range_string(value: str) -> dict[str, datetime] | None:
    stripped = value.strip()
    if len(stripped) < 2:
        return None
    if stripped[0] not in "[(" or stripped[-1] not in "])":
        return None
    body = stripped[1:-1]
    parts = body.split(",", 1)
    if len(parts) != 2:
        return None
    start_text = parts[0].strip().strip('"')
    end_text = parts[1].strip().strip('"')
    if not start_text or not end_text:
        return None
    try:
        start = datetime.fromisoformat(start_text)
        end = datetime.fromisoformat(end_text)
    except ValueError:
        return None
    return {"start": start, "end": end}


class BookingCreate(BaseModel):
    guest_id: UUID
    room_id: UUID
    tz_range: TimeRange


class BookingRead(BaseModel):
    id: UUID
    guest_id: UUID
    room_id: UUID
    tz_range: TimeRange

    model_config = ConfigDict(from_attributes=True)

    @field_validator("tz_range", mode="before")
    @classmethod
    def parse_tz_range(cls, value: Any) -> Any:
        if isinstance(value, TimeRange):
            return value
        if isinstance(value, dict):
            return value
        if value is None:
            return value
        if hasattr(value, "lower") and hasattr(value, "upper"):
            return {"start": value.lower, "end": value.upper}
        if isinstance(value, (list, tuple)) and len(value) == 2:
            return {"start": value[0], "end": value[1]}
        if isinstance(value, str):
            parsed = _parse_range_string(value)
            if parsed is not None:
                return parsed
        return value
