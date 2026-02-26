from __future__ import annotations

from datetime import datetime, timezone
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from db.session import get_session
from main import app
from models.guest import Guest


class FakeResult:
    def __init__(self, guests: list[Guest]):
        self._guests = guests

    def scalars(self):
        return self

    def all(self):
        return list(self._guests)


class FakeSession:
    def __init__(self, guests: list[Guest] | None = None):
        self.guests = list(guests or [])
        self.added: list[Guest] = []

    def add(self, guest: Guest) -> None:
        self.added.append(guest)
        self.guests.append(guest)

    async def commit(self) -> None:
        return None

    async def refresh(self, guest: Guest) -> None:
        if guest.id is None:
            guest.id = uuid.uuid4()
        if guest.created_at is None:
            guest.created_at = datetime.now(timezone.utc)

    async def execute(self, _query) -> FakeResult:
        return FakeResult(self.guests)


def guest_fixture(
    *,
    api_id: int,
    location: str,
    name: str,
    image: str | None = None,
) -> Guest:
    return Guest(
        id=uuid.uuid4(),
        api_id=api_id,
        location=location,
        name=name,
        image=image,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.anyio
async def test_create_guest_returns_payload():
    session = FakeSession()

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/guests",
                json={
                    "api_id": 42,
                    "location": "Lisbon",
                    "name": "Ada Lovelace",
                    "image": "https://example.com/ada.png",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert body["api_id"] == 42
    assert body["location"] == "Lisbon"
    assert body["name"] == "Ada Lovelace"
    assert body["image"] == "https://example.com/ada.png"
    assert body["created_at"]
    assert body["id"]


@pytest.mark.anyio
async def test_list_guests_returns_collection():
    guests = [
        guest_fixture(
            api_id=1,
            location="Tokyo",
            name="Grace Hopper",
            image=None,
        ),
        guest_fixture(
            api_id=2,
            location="Oslo",
            name="Edsger Dijkstra",
            image="https://example.com/edsger.png",
        ),
    ]
    session = FakeSession(guests=guests)

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/guests")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["api_id"] == 1
    assert body[0]["location"] == "Tokyo"
    assert body[0]["name"] == "Grace Hopper"
    assert body[0]["image"] is None
    assert body[0]["created_at"]
    assert body[1]["api_id"] == 2
    assert body[1]["location"] == "Oslo"
    assert body[1]["name"] == "Edsger Dijkstra"
    assert body[1]["image"] == "https://example.com/edsger.png"
    assert body[1]["created_at"]
