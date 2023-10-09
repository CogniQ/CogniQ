from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

import sqlalchemy
from sqlalchemy import Table, MetaData
from sqlalchemy.ext.asyncio import AsyncEngine

from datetime import datetime

from cogniq.config import DATABASE_URL


class TaskStore:
    def __init__(self):
        """
        A queue of tasks to be completed.
        """

        self.database_url = DATABASE_URL
        self.engine: AsyncEngine = sqlalchemy.ext.asyncio.create_async_engine(DATABASE_URL)
        self.metadata = MetaData()
        self.table = Table(
            "tasks",
            self.metadata,
            sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column("future_message", sqlalchemy.String),
            sqlalchemy.Column("when_time", sqlalchemy.DateTime),
        )

    async def async_setup(self) -> None:
        async with self.engine.begin() as conn:

            def get_tables(sync_conn):
                inspector = sqlalchemy.inspect(sync_conn)
                return inspector.get_table_names()

            table_names = await conn.run_sync(get_tables)
            for table in ["tasks"]:
                if table not in table_names:
                    raise Exception(f"Table {table} not found in database. Please run migrations with `.venv/bin/alembic upgrade head`.")

    async def async_enqueue_task(self, *, future_message: str, when_time: datetime, confirmation_response: str) -> str:
        """
        Enqueue a task to be completed at a later time.
        Respond with a confirmation message.
        """
        async with self.engine.begin() as conn:
            result = await conn.execute(self.table.insert().values({"future_message": future_message, "when_time": when_time}))
            if result.rowcount == 1:
                answer = confirmation_response
            else:
                answer = "Failed to enqueue task."
            return answer
