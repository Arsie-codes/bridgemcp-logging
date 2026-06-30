"""TextFormatter — human-readable one-line log output."""

from __future__ import annotations

from .record import InvocationRecord

_LEVEL_WIDTH = 5  # "DEBUG" is 5, "INFO " pads to 5
_LABEL_WIDTH = 40  # primitive:name column width


class TextFormatter:
    """Formats an :class:`~bridgemcp_logging.InvocationRecord` as a single line.

    Output format::

        [2026-06-30 12:00:00Z] INFO  tool:greet           2.1ms  OK
        [2026-06-30 12:00:01Z] ERROR tool:send_email       3.2ms  FAILED  SMTPAuthenticationError: ...

    The timestamp is UTC. The label column (``primitive:name``) is padded to
    40 characters. Duration is rounded to one decimal place.
    """

    def format(self, record: InvocationRecord) -> str:
        ts = record.started_at.strftime("%Y-%m-%d %H:%M:%SZ")
        level = record.level.ljust(_LEVEL_WIDTH)
        label = f"{record.primitive}:{record.name}".ljust(_LABEL_WIDTH)
        duration = f"{record.duration_ms:.1f}ms"
        status = "OK" if record.succeeded else "FAILED"

        line = f"[{ts}] {level}  {label}  {duration}  {status}"

        if not record.succeeded and record.exception_type and record.exception_chain:
            line += f"  {record.exception_chain[0]}"

        return line
