from __future__ import annotations

from datetime import datetime, timezone
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from db.session import get_session
from models.hotel import Hotel, HotelAction


class FakeResult:
    def __init__(self, hotels: list[Hotel]):
        self._hotels = hotels

    def scalars(self):
        return self

    def all(self):
        return list(self._hotels)


class FakeSession:
    def __init__(self, hotels: list[Hotel] | None = None):
        self.hotels = list(hotels or [])
        self.added: list[Hotel] = []

    def add(self, hotel: Hotel) -> None:
        self.added.append(hotel)
        self.hotels.append(hotel)

    async def commit(self) -> None:
        return None

    async def refresh(self, hotel: Hotel) -> None:
        if hotel.id is None:
            hotel.id = uuid.uuid4()
        if hotel.created_at is None:
            hotel.created_at = datetime.now(timezone.utc)

    async def execute(self, _query) -> FakeResult:
        return FakeResult(self.hotels)


def hotel_fixture(
    *,
    name: str,
    location_id: int,
) -> Hotel:
    return Hotel(
        id=uuid.uuid4(),
        name=name,
        location_id=location_id,
        created_at=datetime.now(timezone.utc),
        updated_at=None,
        deleted_at=None,
        action=HotelAction.CREATE,
    )


@pytest.mark.anyio
async def test_create_hotel_returns_payload():
    session = FakeSession()

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/hotels",
                json={"name": "Cafe Plaza", "location_id": 10},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Cafe Plaza"
    assert body["location_id"] == 10
    assert body["action"] == "CREATE"
    assert body["id"]
    assert body["created_at"]
    assert body["updated_at"] is None
    assert body["deleted_at"] is None


@pytest.mark.anyio
async def test_list_hotels_returns_collection():
    hotels = [
        hotel_fixture(name="Aurora", location_id=1),
        hotel_fixture(name="Beacon", location_id=2),
    ]
    session = FakeSession(hotels=hotels)

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/hotels")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["name"] == "Aurora"
    assert body[0]["location_id"] == 1
    assert body[0]["action"] == "CREATE"
    assert body[1]["name"] == "Beacon"
    assert body[1]["location_id"] == 2
    assert body[1]["action"] == "CREATE"
