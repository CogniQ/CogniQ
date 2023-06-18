import logging
import time

from datetime import datetime
from logging import Logger
from typing import Optional
from uuid import uuid4

from databases import Database

from slack_sdk.oauth.state_store.async_state_store import AsyncOAuthStateStore
from slack_sdk.oauth.state_store.sqlalchemy import SQLAlchemyOAuthStateStore

from sqlalchemy import and_, desc, Table, MetaData


class StateStore(AsyncOAuthStateStore):
    database_url: str
    expiration_seconds: int
    metadata: MetaData
    oauth_states: Table

    def __init__(
        self,
        *,
        expiration_seconds: int,
        database_url: str,
        logger: Logger = logging.getLogger(__name__),
    ):
        self.expiration_seconds = expiration_seconds
        self.database_url = database_url
        self._logger = logger
        self.metadata = MetaData()
        self.oauth_states = SQLAlchemyOAuthStateStore.build_oauth_states_table(
            metadata=self.metadata,
            table_name="slack_oauth_states",
        )

    @property
    def logger(self) -> Logger:
        return self._logger

    async def async_issue(self) -> str:
        state: str = str(uuid4())
        now = datetime.utcfromtimestamp(time.time() + self.expiration_seconds)
        async with Database(self.database_url) as database:
            await database.execute(self.oauth_states.insert(), {"state": state, "expire_at": now})
            return state

    async def async_consume(self, state: str) -> bool:
        try:
            async with Database(self.database_url) as database:
                async with database.transaction():
                    c = self.oauth_states.c
                    query = self.oauth_states.select().where(and_(c.state == state, c.expire_at > datetime.utcnow()))
                    row = await database.fetch_one(query)
                    self.logger.debug(f"consume's query result: {row}")
                    await database.execute(self.oauth_states.delete().where(c.id == row["id"]))
                    return True
            return False
        except Exception as e:
            message = f"Failed to find any persistent data for state: {state} - {e}"
            self.logger.warning(message)
            return False
