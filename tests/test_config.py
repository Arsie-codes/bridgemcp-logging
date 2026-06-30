"""Tests for LoggingConfig."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from bridgemcp_logging import LoggingConfig


def test_defaults() -> None:
    config = LoggingConfig()
    assert config.success_level == "INFO"
    assert config.error_level == "ERROR"
    assert config.log_kwargs is False
    assert config.log_result is False


def test_levels_normalised_to_uppercase() -> None:
    config = LoggingConfig(success_level="debug", error_level="warning")
    assert config.success_level == "DEBUG"
    assert config.error_level == "WARNING"


def test_all_valid_levels_accepted() -> None:
    for level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        config = LoggingConfig(success_level=level, error_level=level)
        assert config.success_level == level


def test_invalid_level_raises() -> None:
    with pytest.raises(ValidationError):
        LoggingConfig(success_level="VERBOSE")


def test_invalid_error_level_raises() -> None:
    with pytest.raises(ValidationError):
        LoggingConfig(error_level="TRACE")


def test_frozen_cannot_mutate() -> None:
    config = LoggingConfig()
    with pytest.raises((TypeError, ValidationError)):
        config.success_level = "DEBUG"  # type: ignore[misc]


def test_log_kwargs_and_result_flags() -> None:
    config = LoggingConfig(log_kwargs=True, log_result=True)
    assert config.log_kwargs is True
    assert config.log_result is True
