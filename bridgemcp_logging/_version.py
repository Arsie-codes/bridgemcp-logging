"""Single source of truth for the bridgemcp-logging version string."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

try:
    __version__: str = _pkg_version("bridgemcp-logging")
except PackageNotFoundError:
    # Package not installed (e.g. running directly from source without
    # pip install -e .). "0.0.0" is used instead of a sentinel string so the
    # fallback remains PEP 440 parseable by version-aware tooling.
    __version__ = "0.0.0"
