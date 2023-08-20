from __future__ import annotations
from typing import Literal, Dict, Type, Any
from types import TracebackType
import logging

logger = logging.getLogger(__name__)


from contextlib import AbstractAsyncContextManager

from wandb.sdk.data_types.trace_tree import Trace
from wandb.sdk.wandb_run import Run
from wandb.sdk.lib import RunDisabled
import datetime
import wandb

from cogniq.config import WANDB_PROJECT # type: ignore


class WandbRun(AbstractAsyncContextManager):
    def __init__(
        self,
        *,
        config: Dict[str, Any] = {},
        name: str = "CogniQ",
    ) -> None:
        self.run = wandb.init(
            project=WANDB_PROJECT,
            config={},
        )

        self.name = name  # TODO: add feature to add descriptive name at conclusion of run.

    async def __aenter__(self) -> Run | RunDisabled | None:
        self.start_time_ms = datetime.datetime.now().timestamp() * 1000
        name_prefix = f"{self.name}-" if self.name else ""
        self.root_span = Trace(
            name=f"{name_prefix}root",
            kind="agent",
            start_time_ms=self.start_time_ms,
        )

        return self

    async def __aexit__(self, exc_type: Type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None) -> None:
        self.end_time_ms = round(datetime.datetime.now().timestamp() * 1000)  # logged in milliseconds

        if exc_value:
            wandb.alert(title=exc_type, text=f"{exc_type}: {exc_value}", level="ERROR")

        self.root_span.log(name=self.name)
        wandb.finish(
            exit_code=0 if not exc_value else 1,
        )
