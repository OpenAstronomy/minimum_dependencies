"""Generate a minimum dependencies file for a Python project."""
from ._core import write
from ._version import version as __version__

__all__ = ["write", "__version__"]
