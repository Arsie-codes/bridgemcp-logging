"""ConsoleHandler — writes formatted InvocationRecords to a text stream."""

from __future__ import annotations

import sys
from typing import TextIO

from .record import InvocationRecord
from .text import TextFormatter


class ConsoleHandler:
    """Writes a formatted :class:`~bridgemcp_logging.InvocationRecord` to a
    text stream (default: ``sys.stderr``).

    Each record is written as a single line followed by a newline, then
    immediately flushed. This ensures records appear in order and are not
    lost if the process exits unexpectedly.

    Args:
        stream: Any writable text stream. Resolved to ``sys.stderr`` at
            construction time when not provided, so reassignments to
            ``sys.stderr`` after construction are not reflected.
        formatter: Formatter used to convert records to strings.
            Defaults to :class:`~bridgemcp_logging.TextFormatter`.
    """

    def __init__(
        self,
        stream: TextIO | None = None,
        formatter: TextFormatter | None = None,
    ) -> None:
        self._stream: TextIO = stream if stream is not None else sys.stderr
        self._formatter = formatter if formatter is not None else TextFormatter()

    def emit(self, record: InvocationRecord) -> None:
        """Write *record* to the stream."""
        line = self._formatter.format(record)
        self._stream.write(line + "\n")
        self._stream.flush()

    def flush(self) -> None:
        """Flush the underlying stream."""
        self._stream.flush()
