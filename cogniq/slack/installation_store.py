from __future__ import annotations
from typing import *

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
        database_url: str,
        logger: Logger = logging.getLogger(__name__),
        install_path: str | None = None,
    ):
        self.client_id = client_id
        self.database_url = database_url
        self._logger = logger
        self.install_path = install_path
        self.metadata = MetaData()
        self.installations = SQLAlchemyInstallationStore.build_installations_table(
            metadata=self.metadata,
            table_name="slack_installations",
        )
        self.bots = SQLAlchemyInstallationStore.build_bots_table(
            metadata=self.metadata,
            table_name="slack_bots",
        )

    @property
    def logger(self) -> Logger:
        return self._logger

    async def async_save(self, installation: Installation):
        async with Database(self.database_url) as database:
            async with database.transaction():
                i = installation.to_dict()
                i["client_id"] = self.client_id
                await database.execute(self.installations.insert(), i)
            b = installation.to_bot()
            await self.async_save_bot(b)

    async def async_save_bot(self, bot: Bot):
        """Saves a bot installation data"""
        async with Database(self.database_url) as database:
            async with database.transaction():
                b = bot.to_dict()
                b["client_id"] = self.client_id
                await database.execute(self.bots.insert(), b)

    async def async_find_bot(
        self,
        *,
        enterprise_id: str | None,
        team_id: str | None,
        is_enterprise_install: bool | None,
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
            .order_by(desc(c.installed_at))
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
    ) -> Installation | None:
        """Finds a relevant installation for the given IDs."""
        c = self.installations.c
        conditions = [
            c.enterprise_id == enterprise_id,
            c.team_id == team_id,
            c.is_enterprise_install == is_enterprise_install,
        ]
        if user_id:
            conditions.append(c.user_id == user_id)

        query = self.installations.select().where(and_(*conditions)).order_by(desc(c.installed_at)).limit(1)

        logger.debug("searching for installation: %s" % conditions)

        async with Database(self.database_url) as database:
            i = await database.fetch_one(query)
            # logger.debug("found installation: %s" % i)
            if i:
                return Installation(
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
