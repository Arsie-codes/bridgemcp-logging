"""LoggingPlugin — the primary entry point for bridgemcp-logging."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bridgemcp.plugin import Plugin

from ._version import __version__
from .config import LoggingConfig
from .console import ConsoleHandler
from .middleware import LoggingMiddleware

if TYPE_CHECKING:
    from bridgemcp.application import BridgeMCP


class LoggingPlugin(Plugin):
    """BridgeMCP plugin that logs every tool, resource, and prompt invocation.

    Register as the first plugin so timing covers the full middleware chain::

        app.register_plugin(LoggingPlugin())

    All invocations are written to ``sys.stderr`` by default. Supply a
    custom :class:`~bridgemcp_logging.ConsoleHandler` to redirect output::

        import sys
        from bridgemcp_logging import LoggingPlugin, ConsoleHandler

        app.register_plugin(LoggingPlugin(handler=ConsoleHandler(stream=sys.stdout)))

    Args:
        config: Logging behaviour configuration. Defaults to
            :class:`~bridgemcp_logging.LoggingConfig` with INFO/ERROR levels
            and no argument or result logging.
        handler: Output handler. Defaults to
            :class:`~bridgemcp_logging.ConsoleHandler` writing to
            ``sys.stderr``.
    """

    name = "bridgemcp-logging"
    version: str | None = __version__
    description = "Structured invocation logging for BridgeMCP"
    requires = (">=0.2.1",)

    def __init__(
        self,
        config: LoggingConfig | None = None,
        handler: ConsoleHandler | None = None,
    ) -> None:
        self._config = config if config is not None else LoggingConfig()
        self._handler = handler if handler is not None else ConsoleHandler()
        self._middleware: LoggingMiddleware | None = None

    def setup(self, app: BridgeMCP) -> None:
        """Register the logging middleware with *app*.

        Called immediately by :meth:`~bridgemcp.BridgeMCP.register_plugin`.
        """
        self._middleware = LoggingMiddleware(
            app_name=app.name,
            config=self._config,
            handler=self._handler,
        )
        app.add_middleware(self._middleware)

    async def on_startup(self, app: BridgeMCP) -> None:
        """No-op in v0.1. Reserved for async handler initialisation in future releases."""

    async def on_shutdown(self, app: BridgeMCP) -> None:
        """Flush the handler when the server shuts down."""
        self._handler.flush()
