"""Common test utilities for this package."""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from minimum_dependencies._core import Fail  # pragma: no cover


_TEST = "test"
_TESTING_NO_EXIST = "testing_no_exist"
_TESTING_NO_PIN = "testing_no_pin"
_TESTING_OTHER = "testing_other"
_TESTING_URL = "testing_url"

_FAIL_MSG = {
    "testing_no_exist": r"Exact version .* not found on PyPi.",
    "testing_no_pin": r"No version specifier for .* in install_requires.",
}


def _get_fail_context(fail: "Fail", extras: str) -> pytest.raises:
    if fail:
        return pytest.raises(ValueError, match=_FAIL_MSG[extras])

    return pytest.warns(UserWarning, match=_FAIL_MSG[extras] + r"\nUsing lowest.*")


class _BaseTest:
    """Base class for tests that test against this package."""

    def setup_class(self: "_BaseTest") -> None:
        """Create the truths for testing."""
        self.base = [
            "importlib-metadata==4.11.4\n",
            "packaging==23.0\n",
            "requests==2.25.0\n",
        ]
        self.test = [
            "pytest==6.0.0\n",
            "pytest-doctestplus==0.12.0\n",
        ]
        self.testing_other = [
            "astropy[all]==5.0\n",
            "numpy==1.20.0\n",
            "scipy==1.6.0\n",
        ]
        self.testing_url = [
            "jwst[test] @git+https://github.com/spacetelescope/jwst.git@master\n",
            "stdatamodels @git+https://github.com/spacetelescope/stdatamodels.git@master\n",
        ]
        self.testing_error = [
            "numpy==0.9.6\n",
        ]
