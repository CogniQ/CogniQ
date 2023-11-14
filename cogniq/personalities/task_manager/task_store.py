from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

import sqlalchemy
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    PickleType,
    String,
    Table,
    and_,
    bindparam,
    select,
    text,
)

from sqlalchemy.ext.asyncio import AsyncEngine

from datetime import datetime, timedelta, timezone

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
            Column("id", Integer, primary_key=True),
            Column("future_message", String),
            Column("when_time", DateTime(timezone=True)),
            Column("context", PickleType),
            Column("thread_ts", String, nullable=True),
            Column("status", String, default="ready"),
            Column("locked_at", DateTime(timezone=True), nullable=True),
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

    def current_time(self) -> datetime:
        """
        Get the current time in UTC.
        """
        return datetime.utcnow().replace(tzinfo=timezone.utc)

    async def enqueue_task(
        self,
        *,
        future_message: str,
        when_time: datetime,
        confirmation_response: str,
        context: Dict[str, Any],
        thread_ts: str | None,
    ) -> str:
        """
        Enqueue a task to be completed at a later time.
        Respond with a confirmation message.
        """
        async with self.engine.begin() as conn:
            result = await conn.execute(
                self.table.insert().values(
                    {
                        "future_message": future_message,
                        "when_time": when_time,
                        "context": context,
                        "thread_ts": thread_ts,
                        "status": "ready",
                    }
                )
            )
            if result.rowcount == 1:
                answer = confirmation_response
            else:
                answer = "Failed to enqueue task."
            return answer

    async def dequeue_task(self) -> Dict[str, Any] | None:
        """
        Dequeue tasks that are ready to be completed, handling both PostgreSQL and SQLite databases.
        """
        async with self.engine.begin() as conn:
            query = (
                select(self.table)
                .where(and_(self.table.c.when_time <= bindparam("current_time"), self.table.c.status == bindparam("status")))
                .order_by(self.table.c.when_time)
            )

            # logger.debug(f"Dequeue query: {query}")
            # logger.debug(f"Current time: {current_time}")
            result = await conn.execute(query, {"current_time": self.current_time(), "status": "ready"})

            task = result.fetchone()

            if task is None:
                return None

            dict_task = dict(task)

            if dict_task["when_time"].tzinfo is None:
                """
                This happens when the database does not support timezones, such as SQLite.
                Assume that all datetimes are in UTC.
                """
                dict_task["when_time"] = dict_task["when_time"].replace(tzinfo=timezone.utc)

            return dict_task

    async def lock_task(self, task_id: int) -> Dict[str, Any]:
        """
        Lock a task that is started.
        """
        async with self.engine.begin() as conn:
            result = await conn.execute(
                self.table.update()
                .where(
                    self.table.c.id == task_id,
                    self.table.c.status == "ready",
                )
                .values(
                    status="locked",
                    locked_at=self.current_time(),
                )
            )
            if result.rowcount == 1:
                task = await conn.execute(self.table.select().where(self.table.c.id == task_id))
                return task.fetchone()
            else:
                raise Exception("Failed to lock task. Gone?")

    async def unlock_task(self, task_id: int) -> None:
        """
        Unlock a task that has been abandoned.
        """
        async with self.engine.begin() as conn:
            await conn.execute(
                self.table.update()
                .where(self.table.c.id == task_id)
                .values(
                    status="ready",
                    locked_at=None,
                )
            )

    async def delete_task(self, task_id: int) -> None:
        """
        Delete a task that has been completed.
        """
        async with self.engine.begin() as conn:
            await conn.execute(self.table.delete().where(self.table.c.id == task_id))

    async def reset_orphaned_tasks(self, max_time: int = 600) -> None:
        """
        Reset tasks that have been locked for too long.
        """
        async with self.engine.begin() as conn:
            await conn.execute(
                self.table.update()
                .where(
                    self.table.c.status == "locked",
                    self.table.c.locked_at < self.current_time() - timedelta(seconds=max_time),
                )
                .values(
                    status="ready",
                    locked_at=None,
                )
            )
