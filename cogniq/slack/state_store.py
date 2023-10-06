from __future__ import annotations
from typing import *

import logging

logger = logging.getLogger(__name__)

import time

from datetime import datetime
from logging import Logger
from uuid import uuid4

from slack_sdk.oauth.state_store.async_state_store import AsyncOAuthStateStore
from slack_sdk.oauth.state_store.sqlalchemy import SQLAlchemyOAuthStateStore

import sqlalchemy
from sqlalchemy import and_, desc, Table, MetaData
from sqlalchemy.ext.asyncio import AsyncEngine


class StateStore(AsyncOAuthStateStore):
    engine: AsyncEngine
    expiration_seconds: int
    metadata: MetaData
    oauth_states: Table

    def __init__(self, *, expiration_seconds: int, engine: AsyncEngine):
        self.expiration_seconds = expiration_seconds
        self.engine = engine
        self.metadata = MetaData()
        self.oauth_states = SQLAlchemyOAuthStateStore.build_oauth_states_table(
            metadata=self.metadata,
            table_name="slack_oauth_states",
        )

    async def async_setup(self) -> None:
        pass

    async def async_issue(self) -> str:
        state: str = str(uuid4())
        now = datetime.utcfromtimestamp(time.time() + self.expiration_seconds)
        async with self.engine.begin() as conn:
            await conn.execute(self.oauth_states.insert().values(state=state, expire_at=now))
            return state

    async def async_consume(self, state: str) -> bool:
        try:
            async with self.engine.begin() as conn:
                c = self.oauth_states.c
                query = self.oauth_states.select().where(and_(c.state == state, c.expire_at > datetime.utcnow())).limit(1)
                result = await conn.execute(query)
                row =  result.one_or_none()
                logger.debug(f"consume's query result: {row}")

                if row is None:
                    return False

                await conn.execute(self.oauth_states.delete().where(c.id == row.id))
                return True

            return False
        except Exception as e:
            message = f"Failed to find any persistent data for state: {state} - {e}"
            logger.warning(message)
            return False
