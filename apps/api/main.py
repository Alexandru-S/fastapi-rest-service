import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models.hotel import Hotel, HotelAction
from schemas.hotel import HotelCreate, HotelRead

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
