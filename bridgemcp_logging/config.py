"""Configuration model for bridgemcp-logging."""

from __future__ import annotations

from pydantic import BaseModel, field_validator

_VALID_LEVELS: frozenset[str] = frozenset(
    {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
)


class LoggingConfig(BaseModel, frozen=True):
    """Configuration for :class:`~bridgemcp_logging.LoggingPlugin`.

    All fields have production-safe defaults. ``log_kwargs`` and
    ``log_result`` are ``False`` by default because arguments and return
    values may contain secrets or large payloads — enable them explicitly
    when you need them.

    Attributes:
        success_level: Log level name for successful invocations.
        error_level: Log level name for invocations that raise an exception.
        log_kwargs: Include call arguments in the record.
        log_result: Include the return value in the record.
    """

    success_level: str = "INFO"
    error_level: str = "ERROR"
    log_kwargs: bool = False
    log_result: bool = False

    @field_validator("success_level", "error_level")
    @classmethod
    def _validate_level(cls, v: str) -> str:
        upper = v.upper()
        if upper not in _VALID_LEVELS:
            raise ValueError(
                f"Invalid log level {v!r}. " f"Must be one of: {sorted(_VALID_LEVELS)}"
            )
        return upper
