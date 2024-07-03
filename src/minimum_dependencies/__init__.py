"""Generate a minimum dependencies file for a Python project."""

from ._core import create, write
from ._version import version as __version__

__all__ = ["create", "write", "__version__"]
