import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.dialects.postgresql.ranges import Range
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models.booking import Booking
from models.guest import Guest
from models.hotel import Hotel, HotelAction
from models.room import Room
from schemas.booking import BookingCreate, BookingRead
from schemas.guest import GuestCreate, GuestRead
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


@app.post("/guests", response_model=GuestRead, status_code=201)
async def create_guest(
    payload: GuestCreate,
    session: AsyncSession = Depends(get_session),
):
    guest = Guest(
        api_id=payload.api_id,
        image=payload.image,
        location=payload.location,
        name=payload.name,
    )
    session.add(guest)
    await session.commit()
    await session.refresh(guest)
    return guest


@app.get("/guests", response_model=list[GuestRead])
async def list_guests(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Guest))
    return result.scalars().all()


@app.post("/bookings", response_model=BookingRead, status_code=201)
async def create_booking(
    payload: BookingCreate,
    session: AsyncSession = Depends(get_session),
):
    booking = Booking(
        guest_id=payload.guest_id,
        room_id=payload.room_id,
        tz_range=Range(
            payload.tz_range.start,
            payload.tz_range.end,
            bounds="[)",
        ),
    )
    session.add(booking)
    await session.commit()
    await session.refresh(booking)
    return booking


@app.get("/bookings", response_model=list[BookingRead])
async def list_bookings(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Booking))
    return result.scalars().all()
