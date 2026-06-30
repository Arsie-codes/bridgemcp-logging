"""Tests for ConsoleHandler."""

from __future__ import annotations

import io
from datetime import UTC, datetime
from unittest.mock import MagicMock

from bridgemcp_logging import ConsoleHandler, TextFormatter
from bridgemcp_logging.record import InvocationRecord


def _make_record(**overrides: object) -> InvocationRecord:
    now = datetime(2026, 6, 30, 12, 0, 0, tzinfo=UTC)
    defaults: dict[str, object] = dict(
        invocation_id="x",
        app_name="app",
        framework_version="0.2.1",
        plugin_version="0.1.0",
        primitive="tool",
        name="ping",
        kwargs=None,
        result=None,
        exception=None,
        exception_type=None,
        exception_chain=[],
        succeeded=True,
        duration_ms=1.0,
        started_at=now,
        finished_at=now,
        level="INFO",
    )
    defaults.update(overrides)
    return InvocationRecord(**defaults)  # type: ignore[arg-type]


def test_emit_writes_to_stream() -> None:
    stream = io.StringIO()
    h = ConsoleHandler(stream=stream)
    record = _make_record()
    h.emit(record)
    output = stream.getvalue()
    assert "tool:ping" in output
    assert output.endswith("\n")


def test_emit_flushes_stream() -> None:
    stream = MagicMock(spec=io.StringIO)
    stream.write = MagicMock()
    stream.flush = MagicMock()
    h = ConsoleHandler(stream=stream)
    h.emit(_make_record())
    stream.flush.assert_called()


def test_emit_uses_formatter() -> None:
    stream = io.StringIO()
    fmt = MagicMock(spec=TextFormatter)
    fmt.format = MagicMock(return_value="FORMATTED_LINE")
    h = ConsoleHandler(stream=stream, formatter=fmt)
    record = _make_record()
    h.emit(record)
    fmt.format.assert_called_once_with(record)
    assert "FORMATTED_LINE\n" in stream.getvalue()


def test_flush_calls_stream_flush() -> None:
    stream = MagicMock(spec=io.StringIO)
    stream.flush = MagicMock()
    h = ConsoleHandler(stream=stream)
    h.flush()
    stream.flush.assert_called_once()


def test_default_formatter_produces_text_output() -> None:
    stream = io.StringIO()
    h = ConsoleHandler(stream=stream)  # uses default TextFormatter
    h.emit(_make_record())
    # TextFormatter produces a bracketed timestamp line
    assert "[" in stream.getvalue()
    assert "tool:ping" in stream.getvalue()


def test_multiple_emits_produce_multiple_lines() -> None:
    stream = io.StringIO()
    h = ConsoleHandler(stream=stream)
    h.emit(_make_record(name="tool_a"))
    h.emit(_make_record(name="tool_b"))
    lines = stream.getvalue().splitlines()
    assert len(lines) == 2
    assert "tool_a" in lines[0]
    assert "tool_b" in lines[1]
