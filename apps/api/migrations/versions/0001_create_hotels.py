"""create hotels

Revision ID: 0001_create_hotels
Revises: 
Create Date: 2026-02-08 18:35:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_create_hotels"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'hotel_action') THEN
                CREATE TYPE hotel_action AS ENUM ('CREATE', 'UPDATE', 'DELETE');
            END IF;
        END
        $$;
        """
    )

    hotel_action = postgresql.ENUM(
        "CREATE",
        "UPDATE",
        "DELETE",
        name="hotel_action",
        create_type=False,
    )

    op.create_table(
        "hotels",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("action", hotel_action, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("hotels")
    op.execute("DROP TYPE IF EXISTS hotel_action")
