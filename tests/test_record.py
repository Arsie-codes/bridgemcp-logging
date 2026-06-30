"""Tests for InvocationRecord and extract_chain."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from bridgemcp_logging.record import InvocationRecord, extract_chain


def _make_record(**overrides: object) -> InvocationRecord:
    now = datetime.now(UTC)
    defaults: dict[str, object] = dict(
        invocation_id="test-id",
        app_name="test-app",
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
        duration_ms=5.0,
        started_at=now,
        finished_at=now,
        level="INFO",
    )
    defaults.update(overrides)
    return InvocationRecord(**defaults)  # type: ignore[arg-type]


def test_record_fields_accessible() -> None:
    record = _make_record()
    assert record.invocation_id == "test-id"
    assert record.app_name == "test-app"
    assert record.primitive == "tool"
    assert record.name == "greet"
    assert record.succeeded is True
    assert record.duration_ms == 5.0
    assert record.level == "INFO"


def test_record_is_frozen() -> None:
    record = _make_record()
    with pytest.raises(AttributeError):  # dataclasses.FrozenInstanceError(AttributeError)
        record.name = "other"  # type: ignore[misc]


def test_succeeded_false_when_exception() -> None:
    exc = ValueError("bad input")
    record = _make_record(
        exception=exc,
        exception_type="ValueError",
        exception_chain=["ValueError: bad input"],
        succeeded=False,
        level="ERROR",
    )
    assert record.succeeded is False
    assert record.exception is exc
    assert record.exception_type == "ValueError"
    assert record.level == "ERROR"


def testextract_chain_single_exception() -> None:
    exc = RuntimeError("something broke")
    chain = extract_chain(exc)
    assert len(chain) == 1
    assert "RuntimeError" in chain[0]
    assert "something broke" in chain[0]


def testextract_chain_chained_exception() -> None:
    try:
        try:
            raise ValueError("root cause")
        except ValueError as e:
            raise RuntimeError("wrapped") from e
    except RuntimeError as exc:
        chain = extract_chain(exc)

    assert len(chain) == 2
    assert "RuntimeError" in chain[0]
    assert "ValueError" in chain[1]


def testextract_chain_no_cycle() -> None:
    exc = Exception("lone")
    chain = extract_chain(exc)
    assert len(chain) == 1


def test_record_accepts_all_primitives() -> None:
    for primitive in ("tool", "resource", "prompt"):
        record = _make_record(primitive=primitive)
        assert record.primitive == primitive
