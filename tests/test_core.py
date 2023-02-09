"""Test the _core module."""

import os
import subprocess
import sys
from contextlib import contextmanager
from importlib import import_module
from pathlib import Path

import pytest
import requests
from packaging.requirements import Requirement
from packaging.version import Version

from minimum_dependencies._core import create, minimum_version, versions


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


@contextmanager
def set_dir(path: Path):
    """Set the cwd to the given path for the duration of the context manager."""
    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


@pytest.fixture(scope="class")
def mock_package(tmp_path_factory):
    """Create a mock package for testing."""
    mock_package = tmp_path_factory.mktemp("mock_package")

    # Create some package data
    mock_source = mock_package / "mock_package"
    mock_source.mkdir()
    mock_source.joinpath("__init__.py").touch()

    # create readme
    readme = mock_package / "README.md"
    readme.write_text("This is a mock package for testing.")

    # Create a pyproject.toml
    pyproject = mock_package / "pyproject.toml"
    pyproject.write_text(
        """
    [project]
    name = "mock_package"
    readme = "README.md"
    version = "0.0.1"
    dependencies = [
        "importlib-metadata>=4.11.4",
        "packaging>=19",
        "requests>=2.22",
    ]

    [project.optional-dependencies]
    docs = [
        "sphinx>=3.0"
    ]
    test = [
        "numpy>=1.20",
        "scipy>=1.6",
    ]
    url = [
        "stdatamodels @git+https://github.com/spacetelescope/stdatamodels.git@master"
    ]

    [build-system]
    build-backend = 'setuptools.build_meta'
    requires = [
        "setuptools>=60",
        "setuptools_scm[toml]>=3.4",
        "wheel",
    ]

    [tool.setuptools.packages.find]
    include = ['mock_package']

    """,
    )

    with set_dir(mock_package):
        subprocess.call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                ".",
            ],
        )

    return mock_package


class TestCreate:
    """Test the _core.create function."""

    def setup_class(self):
        """Create truths for testing."""
        self.base_requrirements = [
            "importlib-metadata==4.11.4",
            "packaging==19.0",
            "requests==2.22.0",
        ]
        self.docs_requirements = ["sphinx==3.0.0"]
        self.test_requirements = [
            "numpy==1.20.0",
            "scipy==1.6.0",
        ]
        self.url_requirements = [
            "git+https://github.com/spacetelescope/stdatamodels.git@master",
        ]

    def test_return(self, mock_package):
        """
        Test that the create function returns a string.

        There should be one line per requirement.
        """
        with set_dir(mock_package):
            import_module("mock_package")

            requirements = create("mock_package")
            assert isinstance(requirements, str)
            assert set(requirements.splitlines()) == set(self.base_requrirements)

    def test_extras(self, mock_package):
        """Test that extras dependencies can be included."""
        with set_dir(mock_package):
            import_module("mock_package")

            assert set(
                create("mock_package", extras=["docs", "test"]).splitlines(),
            ) == set(
                self.base_requrirements
                + self.docs_requirements
                + self.test_requirements,
            )

    def test_url(self, mock_package):
        """Test that url dependencies can be included."""
        with set_dir(mock_package):
            import_module("mock_package")

            assert set(
                create("mock_package", extras=["url"]).splitlines(),
            ) == set(
                self.base_requrirements + self.url_requirements,
            )
