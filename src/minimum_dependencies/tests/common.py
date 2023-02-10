"""Common test utilities for this package."""


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
            "stdatamodels @git+https://github.com/spacetelescope/stdatamodels.git@master\n",  # noqa: E501
        ]
