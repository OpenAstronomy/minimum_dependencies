"""Test the _core module."""

import pytest
import requests
from packaging.requirements import Requirement
from packaging.version import Version

from minimum_dependencies._core import minimum_version, versions


class TestVersions:
    """Test the _core.versions function."""

    @staticmethod
    def test_clean_requirement():
        """Test that the versions function returns a list of versions."""
        requirement = Requirement("numpy>=1.20")
        min_length = 113  # 113 versions of numpy on PyPi when writing this

        result = versions(requirement)
        assert isinstance(result, list)
        assert len(result) >= min_length

    @staticmethod
    def test_dirty_requirement():
        """
        Test with a requirement that has a dirty version specifier.

        Make sure versions function still returns a list of versions, even when
        the version specifier for a requirement isn't compatible with packaging's
        Version class. In these cases we will just skip the version.
        """
        requirement = Requirement("poppy>=1.0.2")
        num_releases = len(
            requests.get(
                f"https://pypi.python.org/pypi/{requirement.name}/json",
                timeout=30,
            ).json()["releases"],
        )

        # only one version of poppy is dirty, when this test was written
        assert len(versions(requirement)) <= num_releases - 1

    @staticmethod
    def test_not_requirement():
        """
        Test that versions can handle a requirement that is not on PyPi.

        At time of writing, there is no package called "not-a-package" on PyPi.
        """
        requirement = Requirement("not-a-package>=1.0.2")

        with pytest.raises(ValueError, match=r"Package .* found on PyPi."):
            versions(requirement)

    @staticmethod
    def test_sorted_versions():
        """Test that the versions function returns a sorted list of versions."""
        requirement = Requirement("numpy>=1.20")
        results = versions(requirement)

        # check that this is a list of Versions
        for result in results:
            assert isinstance(result, Version)

        # check that the list is sorted
        for index in range(len(results) - 1):
            assert results[index] < results[index + 1]


class TestMinimumVersion:
    """Test the _core.minimum_version function."""

    def setup_method(self):
        """Create a requirement for testing."""
        self.oldest = Version("0.9.6")
        self.minimum = Version("1.20")
        self.requirement = Requirement(f"numpy>={self.minimum}")

    def test_returns_version(self):
        """Test that the minimum_version function returns a Version."""
        result = minimum_version(self.requirement)
        assert isinstance(result, Version)

    def test_returns_specified_version(self):
        """Test that the minimum_version function returns the specified version."""
        assert minimum_version(self.requirement) == self.minimum

    def test_no_exact_warning(self):
        """
        Test that a warning is issued when the exact version is not found on PyPi.

        Also, test the minimum_version function falls back to the lowest available
        in this case
        """
        requirement = Requirement("numpy>=9.999")

        with pytest.warns(
            UserWarning,
            match=r"Exact version specified .* not found on PyPi.*",
        ):
            assert minimum_version(requirement) == self.oldest

    def test_no_specifier_warning(self):
        """
        Test that a warning is issued when no version specifier is given.

        Also, test the minimum_version function falls back to the lowest available
        in this case.
        """
        requirement = Requirement("numpy")

        with pytest.warns(
            UserWarning,
            match=r"No version specifier for .* in install_requires.*",
        ):
            assert minimum_version(requirement) == self.oldest
