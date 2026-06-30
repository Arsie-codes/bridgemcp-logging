"""Tests for TextFormatter."""

from __future__ import annotations

from datetime import UTC, datetime

from bridgemcp_logging import TextFormatter
from bridgemcp_logging.record import InvocationRecord


def _make_record(**overrides: object) -> InvocationRecord:
    started = datetime(2026, 6, 30, 12, 0, 0, tzinfo=UTC)
    finished = datetime(2026, 6, 30, 12, 0, 0, 12300, tzinfo=UTC)
    defaults: dict[str, object] = dict(
        invocation_id="abc",
        app_name="app",
        framework_version="0.2.1",
        plugin_version="0.1.0",
        primitive="tool",
        name="greet",
        kwargs=None,
        result=None,
        exception=None,
        exception_type=None,
        exception_chain=[],
        succeeded=True,
        duration_ms=12.3,
        started_at=started,
        finished_at=finished,
        level="INFO",
    )
    defaults.update(overrides)
    return InvocationRecord(**defaults)  # type: ignore[arg-type]


def test_success_format_contains_expected_parts(formatter: TextFormatter) -> None:
    record = _make_record()
    line = formatter.format(record)
    assert "[2026-06-30 12:00:00Z]" in line
    assert "INFO" in line
    assert "tool:greet" in line
    assert "12.3ms" in line
    assert "OK" in line
    assert "FAILED" not in line


def test_failure_format_contains_expected_parts(formatter: TextFormatter) -> None:
    exc = ValueError("bad input")
    record = _make_record(
        succeeded=False,
        level="ERROR",
        exception=exc,
        exception_type="ValueError",
        exception_chain=["ValueError: bad input"],
    )
    line = formatter.format(record)
    assert "ERROR" in line
    assert "FAILED" in line
    assert "ValueError: bad input" in line
    assert "OK" not in line


def test_failure_without_exception_chain(formatter: TextFormatter) -> None:
    record = _make_record(
        succeeded=False,
        level="ERROR",
        exception=None,
        exception_type=None,
        exception_chain=[],
    )
    line = formatter.format(record)
    assert "FAILED" in line
    # No exception detail appended when chain is empty
    assert line.endswith("FAILED")


def test_format_returns_single_line(formatter: TextFormatter) -> None:
    record = _make_record()
    line = formatter.format(record)
    assert "\n" not in line


def test_label_contains_primitive_and_name(formatter: TextFormatter) -> None:
    record = _make_record(primitive="resource", name="file://docs/index.md")
    line = formatter.format(record)
    assert "resource:file://docs/index.md" in line


def test_zero_duration(formatter: TextFormatter) -> None:
    record = _make_record(duration_ms=0.0)
    line = formatter.format(record)
    assert "0.0ms" in line


def test_large_duration(formatter: TextFormatter) -> None:
    record = _make_record(duration_ms=9999.9)
    line = formatter.format(record)
    assert "9999.9ms" in line
