"""LoggingMiddleware — timing and exception capture for BridgeMCP invocations."""

from __future__ import annotations

import sys
import uuid
from datetime import UTC, datetime
from time import perf_counter
from typing import TYPE_CHECKING, Any

import bridgemcp
from bridgemcp.middleware import InvocationContext, Next

from ._version import __version__ as _plugin_version
from .config import LoggingConfig
from .console import ConsoleHandler
from .record import InvocationRecord, extract_chain

if TYPE_CHECKING:
    pass


class LoggingMiddleware:
    """Async middleware that records timing and captures exceptions.

    Registered with the BridgeMCP application by
    :class:`~bridgemcp_logging.LoggingPlugin` during ``setup()``.
    Not intended for direct use — instantiate :class:`LoggingPlugin` instead.

    Exceptions raised by the handler are always re-raised after the record
    is emitted. ``asyncio.CancelledError`` and ``KeyboardInterrupt`` are
    not captured because they are not :exc:`Exception` subclasses.

    If record construction or :meth:`~bridgemcp_logging.ConsoleHandler.emit`
    raises, the error is written to ``sys.stderr`` and suppressed — a logging
    failure must never crash the server or mask the original exception.
    """

    def __init__(
        self,
        app_name: str,
        config: LoggingConfig,
        handler: ConsoleHandler,
    ) -> None:
        self._app_name = app_name
        self._config = config
        self._handler = handler
        self._framework_version = bridgemcp.__version__

    async def __call__(self, ctx: InvocationContext, next: Next) -> Any:
        started_at = datetime.now(UTC)
        t0 = perf_counter()

        result: Any = None
        exc: Exception | None = None

        try:
            result = await next(ctx)
        except Exception as e:
            exc = e
            raise
        finally:
            t1 = perf_counter()
            finished_at = datetime.now(UTC)
            duration_ms = (t1 - t0) * 1000.0

            try:
                record = InvocationRecord(
                    invocation_id=str(uuid.uuid4()),
                    app_name=self._app_name,
                    framework_version=self._framework_version,
                    plugin_version=_plugin_version,
                    primitive=ctx.primitive,
                    name=ctx.name,
                    kwargs=dict(ctx.kwargs) if self._config.log_kwargs else None,
                    result=(
                        result if (self._config.log_result and exc is None) else None
                    ),
                    exception=exc,
                    exception_type=type(exc).__name__ if exc is not None else None,
                    exception_chain=extract_chain(exc) if exc is not None else [],
                    succeeded=exc is None,
                    duration_ms=duration_ms,
                    started_at=started_at,
                    finished_at=finished_at,
                    level=(
                        self._config.error_level
                        if exc is not None
                        else self._config.success_level
                    ),
                )
                self._handler.emit(record)
            except Exception:
                print(
                    "bridgemcp-logging: record construction or emit() raised an exception and was suppressed",
                    file=sys.stderr,
                )

        return result
