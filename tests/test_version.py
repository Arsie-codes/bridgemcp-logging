"""Tests for the _version module."""

from __future__ import annotations

import re

import pytest

import bridgemcp_logging._version as _version_module

# PEP 440 release segment: N(.N)* with optional pre/post/dev parts is not
# needed here — the installed version and the fallback are both plain
# release versions, so a simple release-segment pattern is sufficient.
_RELEASE_PATTERN = re.compile(r"^\d+(\.\d+)*$")


def test_installed_version_is_pep440_release() -> None:
    assert _RELEASE_PATTERN.match(_version_module.__version__)


def test_fallback_version_is_pep440_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """When package metadata is unavailable, the fallback must be PEP 440
    parseable ("0.0.0"), not a sentinel string."""
    import importlib.metadata

    def _raise(name: str) -> str:
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", _raise)
    try:
        reloaded = importlib.reload(_version_module)
        assert reloaded.__version__ == "0.0.0"
        assert _RELEASE_PATTERN.match(reloaded.__version__)
    finally:
        monkeypatch.undo()
        importlib.reload(_version_module)
