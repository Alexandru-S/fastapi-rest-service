import uuid

from sqlalchemy import ForeignKey, text
from sqlalchemy.dialects.postgresql import TSTZRANGE, UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    guest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("guests.id"),
        nullable=False,
    )
    room_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rooms.id"),
        nullable=False,
    )
    tz_range: Mapped[object] = mapped_column(TSTZRANGE, nullable=False)
