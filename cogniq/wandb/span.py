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


class WandbSpan(AbstractAsyncContextManager):
    def __init__(self, *, run: Run | RunDisabled, kind: Literal["llm", "agent", "chain", "tool"], name: str) -> None:
        self.run = run
        self.root_span = run.root_span
        self.kind = kind
        self.name = name

    async def __aenter__(self) -> Trace:
        self.start_time_ms = datetime.datetime.now().timestamp() * 1000
        self.span = Trace(
            name=self.name,
            kind=self.kind,
            start_time_ms=self.start_time_ms,
        )

        self.root_span.add_child(self.span)

        return self.span

    async def __aexit__(self, exc_type: Type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None) -> None:
        self.end_time_ms = round(datetime.datetime.now().timestamp() * 1000)  # logged in milliseconds
        self.span.end_time_ms = self.end_time_ms
        
        if exc_value:
            self.span.status_code = "error"
            self.span.status_message = f"{exc_type}: {exc_value}"