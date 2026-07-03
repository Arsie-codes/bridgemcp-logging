# Changelog

All notable changes to `bridgemcp-logging` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [0.1.1] — 2026-07-03

### Fixed

- Added `py.typed` marker (PEP 561) so downstream type checkers recognise the package as fully typed.
  The `Typing :: Typed` classifier was already present in 0.1.0 but the marker was missing from the wheel.
- `ConsoleHandler` now resolves `sys.stderr` at construction time rather than at import time,
  preventing stale-stream writes when `sys.stderr` is reassigned after import (e.g. by pytest capture
  or daemonisation wrappers).
- Record construction in `LoggingMiddleware` is now inside the same suppression guard as `emit()`.
  Previously, an exception whose `__str__` raised during `extract_chain()` would propagate from
  the `finally` block and replace the original tool exception. The logging plugin now guarantees
  it cannot mask or replace any exception from the handler under any circumstances.

## [0.1.0] — 2026-06-30

### Added

- `LoggingPlugin` — BridgeMCP plugin that registers structured invocation logging via middleware.
- `LoggingConfig` — Pydantic frozen configuration model with `success_level`, `error_level`, `log_kwargs`, and `log_result` fields.
- `InvocationRecord` — frozen dataclass carrying timing, exception details, and invocation metadata for every tool, resource, and prompt call.
- `TextFormatter` — human-readable one-line formatter for `InvocationRecord` instances.
- `ConsoleHandler` — writes formatted records to any `TextIO` stream (default: `sys.stderr`).
- `LoggingMiddleware` — async middleware that measures wall-clock timing, captures exceptions, and dispatches records to the configured handler.

[0.1.0]: https://github.com/Arsie-codes/bridgemcp-logging/releases/tag/v0.1.0
