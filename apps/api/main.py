import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models.hotel import Hotel, HotelAction
from models.room import Room
from schemas.hotel import HotelCreate, HotelRead
from schemas.room import RoomCreate, RoomRead

app = FastAPI()

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


@app.post("/hotels", response_model=HotelRead, status_code=201)
async def create_hotel(
    payload: HotelCreate,
    session: AsyncSession = Depends(get_session),
):
    hotel = Hotel(
        name=payload.name,
        location_id=payload.location_id,
        action=HotelAction.CREATE,
    )
    session.add(hotel)
    await session.commit()
    await session.refresh(hotel)
    return hotel


@app.get("/hotels", response_model=list[HotelRead])
async def list_hotels(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Hotel))
    return result.scalars().all()


@app.post("/rooms", response_model=RoomRead, status_code=201)
async def create_room(
    payload: RoomCreate,
    session: AsyncSession = Depends(get_session),
):
    room = Room(
        room_no=payload.room_no,
        name=payload.name,
        floors=payload.floors,
    )
    session.add(room)
    await session.commit()
    await session.refresh(room)
    return room


@app.get("/rooms", response_model=list[RoomRead])
async def list_rooms(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Room))
    return result.scalars().all()
