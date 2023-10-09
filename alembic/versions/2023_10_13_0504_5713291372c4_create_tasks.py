"""create tasks

Revision ID: 5713291372c4
Revises: 4ee29c019291
Create Date: 2023-10-13 05:04:52.298354+00:00

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
revision = "5713291372c4"
down_revision = "4ee29c019291"
branch_labels = None
depends_on = None


def upgrade() -> None:
    table_name = "tasks"
    op.create_table(
        table_name,
        Column("id", Integer, primary_key=True, autoincrement=True),
        # The max length of a slack message is 40000 characters: https://api.slack.com/changelog/2018-04-truncating-really-long-messages
        Column("future_message", String(40000), nullable=False),
        Column("when_time", DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("tasks")
