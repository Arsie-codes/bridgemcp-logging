"""Single source of truth for the bridgemcp-logging version string."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

try:
    __version__: str = _pkg_version("bridgemcp-logging")
except PackageNotFoundError:
    # Package not installed (e.g. running directly from source without pip install -e .)
    __version__ = "__dev__"
