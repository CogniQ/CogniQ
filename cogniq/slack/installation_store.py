from __future__ import annotations
from typing import *
from slack_bolt import BoltContext
from slack_sdk.oauth.installation_store import Installation, Bot

import logging

logger = logging.getLogger(__name__)

import typing
import os
import time
from datetime import datetime
from logging import Logger
from uuid import uuid4

import sqlalchemy
from databases import Database
from slack_sdk.oauth.installation_store import Bot, Installation
from slack_sdk.oauth.installation_store.async_installation_store import (
    AsyncInstallationStore,
)
from slack_sdk.oauth.installation_store.sqlalchemy import SQLAlchemyInstallationStore
from sqlalchemy import and_, desc, Table, MetaData


class InstallationStore(AsyncInstallationStore):
    database_url: str
    client_id: str
    metadata: MetaData
    installations: Table
    bots: Table

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        database_url: str,
        install_path: str | None = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.database_url = database_url
        self._logger = logger
        self.install_path = install_path
        self.token_rotation_expiration_minutes = 60 * 9  # with 9 hours remaining, that's roughly every 3 hours at maximum.
        self.metadata = MetaData()
        self.installations = SQLAlchemyInstallationStore.build_installations_table(
            metadata=self.metadata,
            table_name="slack_installations",
        )
        self.bots = SQLAlchemyInstallationStore.build_bots_table(
            metadata=self.metadata,
            table_name="slack_bots",
        )

        self.engine = sqlalchemy.create_engine(self.database_url)

    async def async_setup(self) -> None:
        try:
            async with Database(self.database_url) as database:
                await database.fetch_one("select count(*) from slack_installations")
        except Exception as e:
            self.metadata.create_all(self.engine)

    @property
    def logger(self) -> Logger:
        return self._logger

    async def async_save(self, installation: Installation) -> None:
        async with Database(self.database_url) as database:
            i = installation.to_dict()
            i["client_id"] = self.client_id
            i_column = self.installations.c

            # check if an installation with these attributes already exists
            installations_row_id: Optional[str] = None
            installations_rows = await database.fetch_all(
                sqlalchemy.select(i_column.id)
                .where(
                    and_(
                        i_column.client_id == self.client_id,
                        i_column.enterprise_id == installation.enterprise_id,
                        i_column.team_id == installation.team_id,
                        i_column.installed_at == i.get("installed_at"),
                    )
                )
                .limit(1)
            )
            for row in installations_rows:
                installations_row_id = row["id"]

            async with database.transaction():
                if installations_row_id is None:
                    await database.execute(self.installations.insert(), i)
                else:
                    update_statement = self.installations.update().where(i_column.id == installations_row_id).values(**i)
                    await database.execute(update_statement)

            # bots
            await self.async_save_bot(installation.to_bot())

    async def async_save_bot(self, bot: Bot) -> None:
        """Saves a bot installation data"""
        async with Database(self.database_url) as database:
            b = bot.to_dict()
            b["client_id"] = self.client_id
            b_column = self.bots.c

            # check if a bot with these attributes already exists
            bots_row_id: Optional[str] = None
            bots_rows = await database.fetch_all(
                sqlalchemy.select(b_column.id)
                .where(
                    and_(
                        b_column.client_id == self.client_id,
                        b_column.enterprise_id == bot.enterprise_id,
                        b_column.team_id == bot.team_id,
                        b_column.installed_at == b.get("installed_at"),
                    )
                )
                .limit(1)
            )
            for row in bots_rows:
                bots_row_id = row["id"]

            async with database.transaction():
                if bots_row_id is None:
                    await database.execute(self.bots.insert(), b)
                else:
                    update_statement = self.bots.update().where(b_column.id == bots_row_id).values(**b)
                    await database.execute(update_statement)

    async def async_find_bot(
        self,
        *,
        enterprise_id: str | None,
        team_id: str | None,
        is_enterprise_install: bool | None = False,
    ) -> Bot | None:
        c = self.bots.c
        query = (
            self.bots.select()
            .where(
                and_(
                    c.enterprise_id == enterprise_id,
                    c.team_id == team_id,
                    c.is_enterprise_install == is_enterprise_install,
                )
            )
            .order_by(desc(c.installed_at), desc(c.id))
            .limit(1)
        )
        async with Database(self.database_url) as database:
            result = await database.fetch_one(query)
            # logger.info("found bot: %s" % result)
            if result:
                return Bot(
                    app_id=result["app_id"],
                    enterprise_id=result["enterprise_id"],
                    team_id=result["team_id"],
                    bot_token=result["bot_token"],
                    bot_id=result["bot_id"],
                    bot_user_id=result["bot_user_id"],
                    bot_scopes=result["bot_scopes"],
                    installed_at=result["installed_at"],
                )
            else:
                return None

    @typing.no_type_check
    async def async_find_installation(
        self,
        *,
        enterprise_id: str | None,
        team_id: str | None,
        user_id: str | None = None,
        is_enterprise_install: bool | None = False,
        needs_user_token: bool = False,
    ) -> Installation | None:
        """Finds a relevant installation for the given IDs."""
        c = self.installations.c
        conditions = [
            c.enterprise_id == enterprise_id,
            c.team_id == team_id,
            c.is_enterprise_install == is_enterprise_install,
        ]
        if user_id:
            logger.debug("searching for installation with user_id: %s" % user_id)
            conditions.append(c.user_id == user_id)
            if needs_user_token:
                conditions.append(c.user_token != None)
        else:
            logger.debug("searching for installation with team_id: %s" % team_id)

        query = self.installations.select().where(and_(*conditions)).order_by(desc(c.installed_at), desc(c.id)).limit(1)

        async with Database(self.database_url) as database:
            i = await database.fetch_one(query)
            if i:
                installation = Installation(
                    app_id=i.app_id,
                    # org / workspace
                    enterprise_id=i.enterprise_id,
                    enterprise_name=i.enterprise_name,
                    enterprise_url=i.enterprise_url,
                    team_id=i.team_id,
                    team_name=i.team_name,
                    # bot
                    bot_token=i.bot_token,
                    bot_id=i.bot_id,
                    bot_user_id=i.bot_user_id,
                    bot_scopes=i.bot_scopes,
                    # only when token rotation is enabled
                    bot_refresh_token=i.bot_refresh_token,
                    # bot_token_expires_in=i.bot_token_expires_in,
                    bot_token_expires_at=i.bot_token_expires_at,
                    # installer
                    user_id=i.user_id,
                    user_token=i.user_token,
                    user_scopes=i.user_scopes,
                    # only when token rotation is enabled
                    user_refresh_token=i.user_refresh_token,
                    # user_token_expires_in=i.user_token_expires_in,
                    user_token_expires_at=i.user_token_expires_at,
                    # incoming webhook
                    incoming_webhook_url=i.incoming_webhook_url,
                    incoming_webhook_channel=i.incoming_webhook_channel,
                    incoming_webhook_channel_id=i.incoming_webhook_channel_id,
                    incoming_webhook_configuration_url=i.incoming_webhook_configuration_url,
                    # org app
                    is_enterprise_install=i.is_enterprise_install,
                    token_type=i.token_type,
                    # timestamps
                    installed_at=i.installed_at,
                    # custom values
                    # custom_values=i.custom_values,
                )
                return installation
            else:
                return None

    async def async_delete_bot(
        self,
        *,
        enterprise_id: str | None,
        team_id: str | None,
    ) -> None:
        """Deletes a bot scope installation per workspace / org"""
        c = self.bots.c
        query = self.bots.delete().where(
            and_(
                c.enterprise_id == enterprise_id,
                c.team_id == team_id,
            )
        )
        async with Database(self.database_url) as database:
            await database.execute(query)

    async def async_delete_installation(
        self,
        *,
        enterprise_id: str | None,
        team_id: str | None,
        user_id: str | None = None,
    ) -> None:
        """Deletes an installation that matches the given IDs"""
        c = self.installations.c
        conditions = [
            c.enterprise_id == enterprise_id,
            c.team_id == team_id,
        ]
        if user_id:
            conditions.append(c.user_id == user_id)

        query = self.installations.delete().where(and_(*conditions))

        async with Database(self.database_url) as database:
            await database.execute(query)

    async def async_delete_all(
        self,
        *,
        enterprise_id: str | None,
        team_id: str | None,
    ):
        """Deletes all installation data for the given workspace / org"""
        await self.async_delete_bot(enterprise_id=enterprise_id, team_id=team_id)
        await self.async_delete_installation(enterprise_id=enterprise_id, team_id=team_id)

    async def async_find_from_context(
        self,
        *,
        context: Dict[str, Any],
        needs_user_token: bool = False,
    ) -> Installation | None:
        enterprise_id = context["enterprise_id"] if "enterprise_id" in context else None
        team_id = context["team_id"] if "team_id" in context else None
        user_id = context["actor_user_id"] if "actor_user_id" in context else None
        is_enterprise_install = context["is_enterprise_install"] if "is_enterprise_install" in context else False
        installation = await self.async_find_installation(
            enterprise_id=enterprise_id,
            team_id=team_id,
            user_id=user_id,
            is_enterprise_install=is_enterprise_install,
            needs_user_token=needs_user_token,
        )
        if installation:
            return installation
        else:
            return None

    async def async_find_user_token(
        self,
        *,
        context: Dict[str, Any],
    ) -> str | None:
        installation = await self.async_find_from_context(context=context, needs_user_token=True)
        if installation is None:
            return None
        return installation.user_token

    async def async_find_bot_token(
        self,
        *,
        context: Dict[str, Any],
    ) -> str | None:
        installation = await self.async_find_from_context(context=context)
        if installation is None:
            return None
        return installation.bot_token
