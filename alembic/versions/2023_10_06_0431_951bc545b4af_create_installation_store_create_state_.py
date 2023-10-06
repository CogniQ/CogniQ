"""create installation_store; create state_store

Revision ID: 951bc545b4af
Revises: 
Create Date: 2023-10-06 04:31:20.142284+00:00

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
revision = "951bc545b4af"
down_revision = None
branch_labels = None
depends_on = None


def build_installations_table() -> None:
    # https://github.com/slackapi/python-slack-sdk/blob/v3.23.0/slack_sdk/oauth/installation_store/sqlalchemy/__init__.py
    table_name = "slack_installations"
    op.create_table(
        table_name,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("client_id", String(32), nullable=False),
        Column("app_id", String(32), nullable=False),
        Column("enterprise_id", String(32)),
        Column("enterprise_name", String(200)),
        Column("enterprise_url", String(200)),
        Column("team_id", String(32)),
        Column("team_name", String(200)),
        Column("bot_token", String(200)),
        Column("bot_id", String(32)),
        Column("bot_user_id", String(32)),
        Column("bot_scopes", String(1000)),
        Column("bot_refresh_token", String(200)),  # added in v3.8.0
        Column("bot_token_expires_at", DateTime),  # added in v3.8.0
        Column("user_id", String(32), nullable=False),
        Column("user_token", String(200)),
        Column("user_scopes", String(1000)),
        Column("user_refresh_token", String(200)),  # added in v3.8.0
        Column("user_token_expires_at", DateTime),  # added in v3.8.0
        Column("incoming_webhook_url", String(200)),
        Column("incoming_webhook_channel", String(200)),
        Column("incoming_webhook_channel_id", String(200)),
        Column("incoming_webhook_configuration_url", String(200)),
        Column("is_enterprise_install", Boolean, default=False, nullable=False),
        Column("token_type", String(32)),
        Column(
            "installed_at",
            DateTime,
            nullable=False,
            default=sqlalchemy.sql.func.now(),  # type: ignore
        ),
        Index(
            f"{table_name}_idx",
            "client_id",
            "enterprise_id",
            "team_id",
            "user_id",
            "installed_at",
        ),
    )


def build_bots_table() -> None:
    table_name = "slack_bots"
    op.create_table(
        table_name,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("client_id", String(32), nullable=False),
        Column("app_id", String(32), nullable=False),
        Column("enterprise_id", String(32)),
        Column("enterprise_name", String(200)),
        Column("team_id", String(32)),
        Column("team_name", String(200)),
        Column("bot_token", String(200)),
        Column("bot_id", String(32)),
        Column("bot_user_id", String(32)),
        Column("bot_scopes", String(1000)),
        Column("bot_refresh_token", String(200)),  # added in v3.8.0
        Column("bot_token_expires_at", DateTime),  # added in v3.8.0
        Column("is_enterprise_install", Boolean, default=False, nullable=False),
        Column(
            "installed_at",
            DateTime,
            nullable=False,
            default=sqlalchemy.sql.func.now(),  # type: ignore
        ),
        Index(
            f"{table_name}_idx",
            "client_id",
            "enterprise_id",
            "team_id",
            "installed_at",
        ),
    )


def upgrade() -> None:
    build_installations_table()
    build_bots_table()


def downgrade() -> None:
    op.drop_table("slack_installations")
    op.drop_table("slack_bots")
