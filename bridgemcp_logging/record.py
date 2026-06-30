"""InvocationRecord — the structured data object emitted for every invocation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


def extract_chain(exc: Exception) -> list[str]:
    """Walk __cause__ / __context__ and collect string representations."""
    chain: list[str] = []
    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None:
        eid = id(current)
        if eid in seen:
            break
        seen.add(eid)
        chain.append(f"{type(current).__name__}: {current}")
        # Explicit chaining (__cause__) takes precedence over implicit (__context__)
        nxt: BaseException | None = current.__cause__ or (
            current.__context__ if not current.__suppress_context__ else None
        )
        current = nxt
    return chain


@dataclass(frozen=True)
class InvocationRecord:
    """Immutable snapshot of a single BridgeMCP invocation.

    Created by :class:`~bridgemcp_logging.LoggingMiddleware` after every
    handler call completes (successfully or with an exception).

    Attributes:
        invocation_id: UUID4 string, unique per call.
        app_name: Value of ``app.name`` at registration time.
        framework_version: ``bridgemcp.__version__`` at registration time.
        plugin_version: ``bridgemcp_logging.__version__`` at registration time.
        primitive: ``"tool"``, ``"resource"``, or ``"prompt"``.
        name: Registered tool name, resource URI, or prompt name.
        kwargs: Copy of call arguments, or ``None`` if ``log_kwargs=False``.
        result: Return value, or ``None`` if ``log_result=False`` or the
            call raised.
        exception: Captured exception, or ``None`` if the call succeeded.
        exception_type: ``type(exception).__name__``, or ``None``.
        exception_chain: String representations of the full exception chain.
        succeeded: ``True`` if no exception was raised.
        duration_ms: Wall-clock time in milliseconds.
        started_at: UTC timestamp when the invocation began.
        finished_at: UTC timestamp when the invocation completed.
        level: ``"INFO"`` for success, ``"ERROR"`` for failure (from config).
    """

    invocation_id: str
    app_name: str
    framework_version: str
    plugin_version: str
    primitive: str
    name: str
    kwargs: dict[str, Any] | None
    result: Any
    exception: Exception | None
    exception_type: str | None
    exception_chain: list[str]
    succeeded: bool
    duration_ms: float
    started_at: datetime
    finished_at: datetime
    level: str
