from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from db.session import get_session
from main import app
from models.room import Room


class FakeResult:
    def __init__(self, rooms: list[Room]):
        self._rooms = rooms

    def scalars(self):
        return self

    def all(self):
        return list(self._rooms)


class FakeSession:
    def __init__(self, rooms: list[Room] | None = None):
        self.rooms = list(rooms or [])
        self.added: list[Room] = []

    def add(self, room: Room) -> None:
        self.added.append(room)
        self.rooms.append(room)

    async def commit(self) -> None:
        return None

    async def refresh(self, room: Room) -> None:
        if room.id is None:
            room.id = uuid.uuid4()

    async def execute(self, _query) -> FakeResult:
        return FakeResult(self.rooms)


def room_fixture(*, room_no: int, floors: int, name: str | None = None) -> Room:
    return Room(
        id=uuid.uuid4(),
        room_no=room_no,
        floors=floors,
        name=name,
    )


@pytest.mark.anyio
async def test_create_room_returns_payload():
    session = FakeSession()

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/rooms",
                json={"room_no": 101, "floors": 1, "name": "Queen Suite"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert body["room_no"] == 101
    assert body["floors"] == 1
    assert body["name"] == "Queen Suite"
    assert body["id"]


@pytest.mark.anyio
async def test_list_rooms_returns_collection():
    rooms = [
        room_fixture(room_no=101, floors=1, name="Queen Suite"),
        room_fixture(room_no=202, floors=2, name=None),
    ]
    session = FakeSession(rooms=rooms)

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/rooms")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["room_no"] == 101
    assert body[0]["floors"] == 1
    assert body[0]["name"] == "Queen Suite"
    assert body[1]["room_no"] == 202
    assert body[1]["floors"] == 2
    assert body[1]["name"] is None
