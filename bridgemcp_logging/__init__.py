"""bridgemcp-logging — Structured invocation logging for BridgeMCP."""

from ._version import __version__ as __version__
from .config import LoggingConfig as LoggingConfig
from .console import ConsoleHandler as ConsoleHandler
from .middleware import LoggingMiddleware as LoggingMiddleware
from .plugin import LoggingPlugin as LoggingPlugin
from .record import InvocationRecord as InvocationRecord
from .text import TextFormatter as TextFormatter

__all__ = [
    "__version__",
    "LoggingPlugin",
    "LoggingConfig",
    "InvocationRecord",
    "TextFormatter",
    "ConsoleHandler",
    "LoggingMiddleware",
]
