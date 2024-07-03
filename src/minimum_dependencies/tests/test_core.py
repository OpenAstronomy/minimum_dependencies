"""Test the _core module."""

import pytest
import requests
from packaging.requirements import Requirement
from packaging.version import Version

from minimum_dependencies._core import Fail, create, minimum_version, versions, write

from .common import (
    _TEST,
    _TESTING_NO_EXIST,
    _TESTING_NO_PIN,
    _TESTING_OTHER,
    _TESTING_URL,
    _BaseTest,
    _get_fail_context,
)

OLD_REQUESTS = Version(requests.__version__) < Version("2.28.2")


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
    @pytest.mark.skipif(
        OLD_REQUESTS,
        reason="Requests changed something that necessitated handling dirty versions.",
    )
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
                f"https://pypi.org/pypi/{requirement.name}/json",
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

    @pytest.mark.parametrize("fail", Fail)
    @pytest.mark.parametrize("extras", [_TESTING_NO_EXIST, _TESTING_NO_PIN])
    def test_warning_or_error(self, fail, extras):
        """
        Test that an error/warning is issued when requirements are incorrect.

        Also, test the minimum_version function falls back to the lowest available
        in this case.

        Errors/warnings are issues when:
            - the exact version is not found on PyPi.
            - no version specifier is given.
        """
        specifier = "numpy>=999.999.999" if extras == _TESTING_NO_EXIST else "numpy"

        with _get_fail_context(fail, extras):
            assert minimum_version(Requirement(specifier), fail=fail) == self.oldest


class TestCreate(_BaseTest):
    """Test the _core.create function."""

    def test_return(self):
        """
        Test that the create function returns a list of strings.

        There should be one line per requirement.
        """
        requirements = create("minimum-dependencies")

        assert isinstance(requirements, list)
        for requirement in requirements:
            assert isinstance(requirement, str)
            assert set(requirements) == set(self.base)

    def test_extras(self):
        """Test that extras dependencies can be included."""
        assert set(
            create("minimum-dependencies", extras=[_TEST, _TESTING_OTHER]),
        ) == set(self.base_extras + self.test + self.testing_other)

    def test_url(self):
        """Test that url dependencies can be included."""
        assert set(
            create("minimum-dependencies", extras=[_TESTING_URL]),
        ) == set(self.base_extras + self.testing_url)

    @staticmethod
    def test_empty():
        """Test that a package with no requirements returns an empty list."""
        assert create("packaging") == []

    @pytest.mark.parametrize("fail", Fail)
    @pytest.mark.parametrize("extras", [_TESTING_NO_EXIST, _TESTING_NO_PIN])
    def test_warning_or_error(self, fail, extras):
        """
        Test that an error/warning is issued when requirements are incorrect.

        Errors/warnings are issues when:
            - the exact version is not found on PyPi.
            - no version specifier is given.
        """
        with _get_fail_context(fail, extras):
            assert set(
                create("minimum-dependencies", extras=[extras], fail=fail),
            ) == set(self.base_extras + self.testing_error)


class TestWrite(_BaseTest):
    """Test the _core.write function."""

    def test_stout(self, capsys):
        """Test writing to stdout."""
        write("minimum-dependencies", extras=[_TEST, _TESTING_OTHER, _TESTING_URL])
        assert capsys.readouterr().out == "".join(
            create(
                "minimum-dependencies",
                extras=[_TEST, _TESTING_OTHER, _TESTING_URL],
            ),
        )

    def test_filename(self, tmp_path, capsys):
        """Test writing to a file."""
        filename = tmp_path / "requirements-min.txt"

        write(
            "minimum-dependencies",
            filename=filename,
            extras=[_TEST, _TESTING_OTHER, _TESTING_URL],
        )
        assert not capsys.readouterr().out

        with filename.open("r") as f:
            assert f.read() == "".join(
                create(
                    "minimum-dependencies",
                    extras=[_TEST, _TESTING_OTHER, _TESTING_URL],
                ),
            )
