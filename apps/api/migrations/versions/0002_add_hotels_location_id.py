"""add hotels location id

Revision ID: 0002_add_hotels_location_id
Revises: 0001_create_hotels
Create Date: 2026-02-08 19:00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002_add_hotels_location_id"
down_revision: Union[str, None] = "0001_create_hotels"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "hotels",
        sa.Column("location_id", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("hotels", "location_id")
