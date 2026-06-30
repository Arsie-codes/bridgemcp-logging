"""Shared fixtures for bridgemcp-logging tests."""

from __future__ import annotations

import io

import pytest

from bridgemcp_logging import ConsoleHandler, LoggingConfig, TextFormatter


@pytest.fixture()
def captured_stream() -> io.StringIO:
    """A StringIO stream for capturing ConsoleHandler output."""
    return io.StringIO()


@pytest.fixture()
def handler(captured_stream: io.StringIO) -> ConsoleHandler:
    """ConsoleHandler writing to a captured StringIO stream."""
    return ConsoleHandler(stream=captured_stream)


@pytest.fixture()
def default_config() -> LoggingConfig:
    return LoggingConfig()


@pytest.fixture()
def formatter() -> TextFormatter:
    return TextFormatter()
