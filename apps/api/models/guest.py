import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from db.base import Base


class Guest(Base):
    __tablename__ = "guests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    api_id: Mapped[int] = mapped_column(Integer, nullable=False)
    image: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
