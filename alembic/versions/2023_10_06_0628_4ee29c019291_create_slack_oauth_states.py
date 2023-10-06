"""create slack_oauth_states

Revision ID: 4ee29c019291
Revises: 951bc545b4af
Create Date: 2023-10-06 06:28:19.413095+00:00

"""
from alembic import op
import sqlalchemy
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Index,
    Integer,
    String,
)


# revision identifiers, used by Alembic.
revision = "4ee29c019291"
down_revision = "951bc545b4af"
branch_labels = None
depends_on = None


def upgrade() -> None:
    table_name = "slack_oauth_states"
    op.create_table(
        table_name,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("state", String(200), nullable=False),
        Column("expire_at", DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("slack_oauth_states")
