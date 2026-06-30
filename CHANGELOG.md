# Changelog

All notable changes to `bridgemcp-logging` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [0.1.0] — 2026-06-30

### Added

- `LoggingPlugin` — BridgeMCP plugin that registers structured invocation logging via middleware.
- `LoggingConfig` — Pydantic frozen configuration model with `success_level`, `error_level`, `log_kwargs`, and `log_result` fields.
- `InvocationRecord` — frozen dataclass carrying timing, exception details, and invocation metadata for every tool, resource, and prompt call.
- `TextFormatter` — human-readable one-line formatter for `InvocationRecord` instances.
- `ConsoleHandler` — writes formatted records to any `TextIO` stream (default: `sys.stderr`).
- `LoggingMiddleware` — async middleware that measures wall-clock timing, captures exceptions, and dispatches records to the configured handler.

[0.1.0]: https://github.com/Arsie-codes/bridgemcp-logging/releases/tag/v0.1.0
