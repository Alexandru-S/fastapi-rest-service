from __future__ import annotations

from datetime import datetime, timezone
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects.postgresql.ranges import Range

from db.session import get_session
from main import app
from models.booking import Booking


class FakeResult:
    def __init__(self, bookings: list[Booking]):
        self._bookings = bookings

    def scalars(self):
        return self

    def all(self):
        return list(self._bookings)


class FakeSession:
    def __init__(self, bookings: list[Booking] | None = None):
        self.bookings = list(bookings or [])
        self.added: list[Booking] = []

    def add(self, booking: Booking) -> None:
        self.added.append(booking)
        self.bookings.append(booking)

    async def commit(self) -> None:
        return None

    async def refresh(self, booking: Booking) -> None:
        if booking.id is None:
            booking.id = uuid.uuid4()

    async def execute(self, _query) -> FakeResult:
        return FakeResult(self.bookings)


def booking_fixture(
    *,
    guest_id: uuid.UUID,
    room_id: uuid.UUID,
    start: datetime,
    end: datetime,
) -> Booking:
    return Booking(
        id=uuid.uuid4(),
        guest_id=guest_id,
        room_id=room_id,
        tz_range=Range(start, end, bounds="[)"),
    )


@pytest.mark.anyio
async def test_create_booking_returns_payload():
    session = FakeSession()

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    guest_id = uuid.uuid4()
    room_id = uuid.uuid4()
    start = datetime(2026, 2, 27, 12, 0, 0, tzinfo=timezone.utc)
    end = datetime(2026, 2, 28, 12, 0, 0, tzinfo=timezone.utc)
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/bookings",
                json={
                    "guest_id": str(guest_id),
                    "room_id": str(room_id),
                    "tz_range": {
                        "start": start.isoformat(),
                        "end": end.isoformat(),
                    },
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert body["guest_id"] == str(guest_id)
    assert body["room_id"] == str(room_id)
    assert body["tz_range"]["start"] == start.isoformat()
    assert body["tz_range"]["end"] == end.isoformat()
    assert body["id"]


@pytest.mark.anyio
async def test_list_bookings_returns_collection():
    start = datetime(2026, 2, 27, 12, 0, 0, tzinfo=timezone.utc)
    end = datetime(2026, 2, 28, 12, 0, 0, tzinfo=timezone.utc)
    bookings = [
        booking_fixture(
            guest_id=uuid.uuid4(),
            room_id=uuid.uuid4(),
            start=start,
            end=end,
        ),
        booking_fixture(
            guest_id=uuid.uuid4(),
            room_id=uuid.uuid4(),
            start=start,
            end=end,
        ),
    ]
    session = FakeSession(bookings=bookings)

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/bookings")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["guest_id"] == str(bookings[0].guest_id)
    assert body[0]["room_id"] == str(bookings[0].room_id)
    assert body[0]["tz_range"]["start"] == start.isoformat()
    assert body[0]["tz_range"]["end"] == end.isoformat()
    assert body[1]["guest_id"] == str(bookings[1].guest_id)
    assert body[1]["room_id"] == str(bookings[1].room_id)
    assert body[1]["tz_range"]["start"] == start.isoformat()
    assert body[1]["tz_range"]["end"] == end.isoformat()
