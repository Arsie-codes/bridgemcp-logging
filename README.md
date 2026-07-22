# bridgemcp-logging

Structured invocation logging for [BridgeMCP](https://github.com/Arsie-codes/bridgemcp).

Every tool call, resource read, and prompt render is recorded with timing, exception details, and a structured log record. Zero configuration required.

---

## Installation

```
pip install bridgemcp-logging
```

Requires `bridgemcp-py >= 0.2.1` and Python 3.11+.

---

## Quickstart

```python
from bridgemcp import BridgeMCP
from bridgemcp_logging import LoggingPlugin

app = BridgeMCP(name="my-server")
app.register_plugin(LoggingPlugin())

@app.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

app.run()
```

Console output for each call:

```
[2026-06-30 12:00:00Z] INFO  tool:greet           2.1ms  OK
```

---

## Configuration

```python
import sys

from bridgemcp_logging import LoggingPlugin, LoggingConfig, ConsoleHandler

plugin = LoggingPlugin(
    config=LoggingConfig(
        success_level="DEBUG",   # level for successful calls (default: "INFO")
        error_level="ERROR",     # level for failed calls (default: "ERROR")
        log_kwargs=True,         # include call arguments in the record (default: False)
        log_result=False,        # include return values in the record (default: False)
    ),
    handler=ConsoleHandler(stream=sys.stdout),
)
app.register_plugin(plugin)
```

`log_kwargs` and `log_result` are `False` by default because arguments and return values may contain secrets or large payloads. Enable them explicitly when needed.

---

## Public API

### `LoggingPlugin`

```python
class LoggingPlugin(Plugin):
    name = "bridgemcp-logging"
    version: str          # from installed package metadata
    description: str

    def __init__(
        self,
        config: LoggingConfig | None = None,   # defaults to LoggingConfig()
        handler: ConsoleHandler | None = None, # defaults to ConsoleHandler()
    ) -> None: ...

    def setup(self, app: BridgeMCP) -> None: ...
    async def on_startup(self, app: BridgeMCP) -> None: ...
    async def on_shutdown(self, app: BridgeMCP) -> None: ...
```

### `LoggingConfig`

```python
class LoggingConfig(BaseModel, frozen=True):
    success_level: str = "INFO"
    error_level: str = "ERROR"
    log_kwargs: bool = False
    log_result: bool = False
```

### `InvocationRecord`

```python
@dataclass(frozen=True)
class InvocationRecord:
    invocation_id: str
    app_name: str
    framework_version: str
    plugin_version: str
    primitive: str              # "tool" | "resource" | "prompt"
    name: str
    kwargs: dict[str, Any] | None
    result: Any
    exception: Exception | None
    exception_type: str | None
    exception_chain: list[str]
    succeeded: bool
    duration_ms: float
    started_at: datetime
    finished_at: datetime
    level: str
```

### `TextFormatter`

```python
class TextFormatter:
    def format(self, record: InvocationRecord) -> str: ...
```

Produces one-line human-readable output:

```
[2026-06-30 12:00:00Z] INFO  tool:greet           12.3ms  OK
[2026-06-30 12:00:01Z] ERROR tool:send_email        3.2ms  FAILED  SMTPAuthenticationError: ...
```

### `ConsoleHandler`

```python
class ConsoleHandler:
    def __init__(
        self,
        stream: TextIO | None = None,          # defaults to sys.stderr at construction time
        formatter: TextFormatter | None = None, # defaults to TextFormatter()
    ) -> None: ...

    def emit(self, record: InvocationRecord) -> None: ...
    def flush(self) -> None: ...
```

---

## Exception handling

If a tool, resource, or prompt handler raises, the exception is captured in the `InvocationRecord`, the record is emitted, and the exception is re-raised. The logging plugin is transparent — it never swallows exceptions.

`asyncio.CancelledError` and `KeyboardInterrupt` are not captured (they are not `Exception` subclasses and should propagate without interference).

---

## Middleware ordering

`bridgemcp-logging` should be the **first** plugin registered so its timing measurement covers the full middleware chain:

```python
app.register_plugin(LoggingPlugin())   # outermost — measures total wall time
app.register_plugin(AuthPlugin())
app.register_plugin(RateLimitPlugin())
```

---

## Versioning

`bridgemcp-logging` is versioned independently from `bridgemcp-py`. Compatible versions:

| bridgemcp-logging | bridgemcp-py |
|---|---|
| 0.1.x | >= 0.2.1 |

---

## License

MIT — see [LICENSE](LICENSE).

---

# Official BridgeMCP Ecosystem

## Framework

- **BridgeMCP**
  https://github.com/Arsie-codes/bridgemcp

## Official Plugins

- **bridgemcp-logging**
  https://github.com/Arsie-codes/bridgemcp-logging

## Official Servers

- **bridgemcp-server-weather**
  https://github.com/Arsie-codes/bridgemcp-server-weather

More official plugins and servers are currently under development.
