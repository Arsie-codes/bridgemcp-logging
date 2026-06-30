"""Tests for LoggingMiddleware."""

from __future__ import annotations

import io
from typing import Any

import pytest
from bridgemcp.middleware import InvocationContext

from bridgemcp_logging import ConsoleHandler, LoggingConfig
from bridgemcp_logging.middleware import LoggingMiddleware
from bridgemcp_logging.record import InvocationRecord


class _CapturingHandler(ConsoleHandler):
    """ConsoleHandler that collects records for assertion."""

    def __init__(self) -> None:
        super().__init__(stream=io.StringIO())
        self.records: list[InvocationRecord] = []

    def emit(self, record: InvocationRecord) -> None:
        self.records.append(record)
        super().emit(record)


def _mw_with_capture(
    config: LoggingConfig | None = None,
) -> tuple[LoggingMiddleware, _CapturingHandler]:
    cap = _CapturingHandler()
    mw = LoggingMiddleware(
        app_name="test-app",
        config=config if config is not None else LoggingConfig(),
        handler=cap,
    )
    return mw, cap


def _ctx(
    primitive: str = "tool", name: str = "greet", **kwargs: Any
) -> InvocationContext:
    return InvocationContext(primitive=primitive, name=name, kwargs=dict(kwargs))  # type: ignore[arg-type]


async def _success_next(ctx: InvocationContext) -> str:
    return "hello"


async def _failing_next(ctx: InvocationContext) -> str:
    raise ValueError("boom")


async def test_timing_is_positive() -> None:
    mw, cap = _mw_with_capture()
    await mw(_ctx(), _success_next)
    assert len(cap.records) == 1
    assert cap.records[0].duration_ms >= 0.0


async def test_success_record_fields() -> None:
    mw, cap = _mw_with_capture()
    result = await mw(_ctx(name="ping"), _success_next)

    assert result == "hello"
    rec = cap.records[0]
    assert rec.succeeded is True
    assert rec.exception is None
    assert rec.exception_type is None
    assert rec.exception_chain == []
    assert rec.level == "INFO"
    assert rec.primitive == "tool"
    assert rec.name == "ping"
    assert rec.app_name == "test-app"


async def test_exception_is_captured_and_reraised() -> None:
    mw, cap = _mw_with_capture()

    with pytest.raises(ValueError, match="boom"):
        await mw(_ctx(), _failing_next)

    assert len(cap.records) == 1
    rec = cap.records[0]
    assert rec.succeeded is False
    assert isinstance(rec.exception, ValueError)
    assert rec.exception_type == "ValueError"
    assert rec.level == "ERROR"
    assert len(rec.exception_chain) >= 1


async def test_log_kwargs_false_gives_none() -> None:
    mw, cap = _mw_with_capture(config=LoggingConfig(log_kwargs=False))
    await mw(_ctx(name="x", foo="bar"), _success_next)
    assert cap.records[0].kwargs is None


async def test_log_kwargs_true_captures_kwargs() -> None:
    mw, cap = _mw_with_capture(config=LoggingConfig(log_kwargs=True))
    await mw(_ctx(name="x", foo="bar"), _success_next)
    assert cap.records[0].kwargs == {"foo": "bar"}


async def test_log_result_false_gives_none() -> None:
    mw, cap = _mw_with_capture(config=LoggingConfig(log_result=False))
    await mw(_ctx(), _success_next)
    assert cap.records[0].result is None


async def test_log_result_true_captures_return_value() -> None:
    mw, cap = _mw_with_capture(config=LoggingConfig(log_result=True))
    await mw(_ctx(), _success_next)
    assert cap.records[0].result == "hello"


async def test_result_is_none_when_exception_even_if_log_result_true() -> None:
    mw, cap = _mw_with_capture(config=LoggingConfig(log_result=True))
    with pytest.raises(ValueError):
        await mw(_ctx(), _failing_next)
    assert cap.records[0].result is None


async def test_invocation_id_is_unique_per_call() -> None:
    mw, cap = _mw_with_capture()
    await mw(_ctx(), _success_next)
    await mw(_ctx(), _success_next)
    assert cap.records[0].invocation_id != cap.records[1].invocation_id


async def test_emit_error_is_suppressed(capsys: Any) -> None:
    """Handler.emit() exceptions must not propagate."""

    class _BrokenHandler(ConsoleHandler):
        def emit(self, record: InvocationRecord) -> None:
            raise RuntimeError("disk full")

    mw = LoggingMiddleware(
        app_name="app",
        config=LoggingConfig(),
        handler=_BrokenHandler(stream=io.StringIO()),
    )
    result = await mw(_ctx(), _success_next)
    assert result == "hello"

    captured_err = capsys.readouterr().err
    assert "bridgemcp-logging" in captured_err


async def test_writes_to_stream_on_success() -> None:
    stream = io.StringIO()
    mw = LoggingMiddleware(
        app_name="app",
        config=LoggingConfig(),
        handler=ConsoleHandler(stream=stream),
    )
    await mw(_ctx(name="say_hi"), _success_next)
    output = stream.getvalue()
    assert "tool:say_hi" in output
    assert "OK" in output


async def test_writes_to_stream_on_failure() -> None:
    stream = io.StringIO()
    mw = LoggingMiddleware(
        app_name="app",
        config=LoggingConfig(),
        handler=ConsoleHandler(stream=stream),
    )
    with pytest.raises(ValueError):
        await mw(_ctx(name="explode"), _failing_next)
    output = stream.getvalue()
    assert "tool:explode" in output
    assert "FAILED" in output
