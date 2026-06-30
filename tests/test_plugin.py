"""Integration tests for LoggingPlugin with a real BridgeMCP app."""

from __future__ import annotations

import io

import pytest
from bridgemcp import BridgeMCP

from bridgemcp_logging import ConsoleHandler, LoggingConfig, LoggingPlugin
from bridgemcp_logging.record import InvocationRecord


class _CapturingHandler(ConsoleHandler):
    """ConsoleHandler subclass that collects records for assertion."""

    def __init__(self) -> None:
        super().__init__(stream=io.StringIO())
        self.records: list[InvocationRecord] = []

    def emit(self, record: InvocationRecord) -> None:
        self.records.append(record)
        super().emit(record)


@pytest.fixture()
def capturing_handler() -> _CapturingHandler:
    return _CapturingHandler()


@pytest.fixture()
def app_with_plugin(
    capturing_handler: _CapturingHandler,
) -> tuple[BridgeMCP, _CapturingHandler]:
    app = BridgeMCP(name="test-server")
    plugin = LoggingPlugin(config=LoggingConfig(), handler=capturing_handler)
    app.register_plugin(plugin)

    @app.tool
    def greet(name: str) -> str:  # type: ignore[reportUnusedFunction]
        return f"Hello, {name}!"

    @app.tool
    def fail_tool() -> str:  # type: ignore[reportUnusedFunction]
        raise RuntimeError("tool failed")

    return app, capturing_handler


def test_tool_call_produces_record(
    app_with_plugin: tuple[BridgeMCP, _CapturingHandler],
) -> None:
    app, handler = app_with_plugin
    app.call("greet", name="World")
    assert len(handler.records) == 1
    rec = handler.records[0]
    assert rec.primitive == "tool"
    assert rec.name == "greet"
    assert rec.succeeded is True
    assert rec.level == "INFO"
    assert rec.app_name == "test-server"
    assert rec.duration_ms >= 0.0
    assert rec.invocation_id != ""


def test_failed_tool_produces_error_record(
    app_with_plugin: tuple[BridgeMCP, _CapturingHandler],
) -> None:
    from bridgemcp.exceptions import ToolExecutionError

    app, handler = app_with_plugin
    with pytest.raises(ToolExecutionError):
        app.call("fail_tool")
    assert len(handler.records) == 1
    rec = handler.records[0]
    assert rec.succeeded is False
    assert rec.level == "ERROR"
    assert rec.exception_type is not None
    assert len(rec.exception_chain) >= 1


def test_multiple_calls_produce_multiple_records(
    app_with_plugin: tuple[BridgeMCP, _CapturingHandler],
) -> None:
    app, handler = app_with_plugin
    app.call("greet", name="Alice")
    app.call("greet", name="Bob")
    assert len(handler.records) == 2
    assert handler.records[0].invocation_id != handler.records[1].invocation_id


def test_record_framework_version_is_populated(
    app_with_plugin: tuple[BridgeMCP, _CapturingHandler],
) -> None:
    import bridgemcp

    app, handler = app_with_plugin
    app.call("greet", name="test")
    rec = handler.records[0]
    assert rec.framework_version == bridgemcp.__version__
    assert rec.framework_version != ""


def test_kwargs_not_logged_by_default(
    app_with_plugin: tuple[BridgeMCP, _CapturingHandler],
) -> None:
    app, handler = app_with_plugin
    app.call("greet", name="secret")
    assert handler.records[0].kwargs is None


def test_kwargs_logged_when_enabled() -> None:
    capturing = _CapturingHandler()
    app = BridgeMCP(name="kw-app")
    app.register_plugin(
        LoggingPlugin(config=LoggingConfig(log_kwargs=True), handler=capturing)
    )

    @app.tool
    def echo(msg: str) -> str:  # type: ignore[reportUnusedFunction]
        return msg

    app.call("echo", msg="hello")
    assert capturing.records[0].kwargs == {"msg": "hello"}


def test_plugin_name_and_metadata() -> None:
    plugin = LoggingPlugin()
    assert plugin.name == "bridgemcp-logging"
    assert plugin.version is not None
    assert plugin.description != ""


async def test_async_tool_call_produces_record() -> None:
    capturing = _CapturingHandler()
    app = BridgeMCP(name="async-app")
    app.register_plugin(LoggingPlugin(handler=capturing))

    @app.tool
    async def async_greet(name: str) -> str:  # type: ignore[reportUnusedFunction]
        return f"Hi, {name}!"

    await app.acall("async_greet", name="World")
    assert len(capturing.records) == 1
    rec = capturing.records[0]
    assert rec.succeeded is True
    assert rec.name == "async_greet"


async def test_on_shutdown_flushes_handler() -> None:
    """on_shutdown must call handler.flush() without raising."""
    app = BridgeMCP(name="shutdown-app")
    flush_called = False

    class _TrackingHandler(ConsoleHandler):
        def flush(self) -> None:
            nonlocal flush_called
            flush_called = True

    plugin = LoggingPlugin(handler=_TrackingHandler(stream=io.StringIO()))
    app.register_plugin(plugin)
    await plugin.on_shutdown(app)
    assert flush_called
