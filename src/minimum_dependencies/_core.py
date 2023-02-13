"""Core functionality for minimum_dependencies."""

import sys
import warnings
from contextlib import suppress
from enum import Flag
from pathlib import Path
from typing import List

import requests
from importlib_metadata import requires
from packaging.requirements import Requirement
from packaging.version import InvalidVersion, Version, parse


def versions(requirement: Requirement) -> List[Version]:
    """
    Get the versions available on PyPi for a given requirement.

    Parameters
    ----------
    requirement : Requirement
        The requirement to get the versions for.

    Returns
    -------
    A sorted list of versions available on PyPi for the given requirement.
    """
    content = requests.get(
        f"https://pypi.python.org/pypi/{requirement.name}/json",
        timeout=30,
    ).json()

    if "releases" not in content:
        msg = f"Package {requirement.name} not found on PyPi."
        raise ValueError(msg)

    versions = []
    for v in content["releases"]:
        with suppress(InvalidVersion):
            versions.append(parse(v))

    return sorted(versions)


class Fail(Flag):
    """Define the error handling behavior for minimum_version."""

    TRUE = True
    FALSE = False


def minimum_version(requirement: Requirement, fail: Fail = Fail.FALSE) -> Version:
    """
    Return minimum version available on PyPi for a given version specification.

    Note: this will fall back on the oldest version available on PyPi if there
    is no version available that matches the version specification. Or no specification
    found at all.

    Parameters
    ----------
    requirement : Requirement
        The requirement to get the versions for.
    fail : Fail, optional
        If an error is raised when the exact version is not found on PyPi. If False,
        a warning will be issued and the lowest available version will be returned.
        Default is False.

    Returns
    -------
    The minimum version available on PyPi for the given requirement.
    """
    if not requirement.specifier:
        msg = f'Could not parse a version specifier from {requirement.name}'
        if fail:
            raise ValueError(msg)

        warnings.warn(msg, stacklevel=2)

    for version in (versions_ := versions(requirement)):
        if version in requirement.specifier:
            # If the requirement does not list any version, the lowest will be
            return version

    # If the specified version does not exist on PyPi, issue a warning
    # and return the lowest available version
    msg = f'Could not find {requirement} on PyPi'
    if fail:
        raise ValueError(msg)

    version = versions_[0]

    msg += f"; using lowest available version: {version}"
    warnings.warn(msg, stacklevel=2)

    return versions_[0]


def create(package: str, extras: list = None, fail: Fail = Fail.FALSE) -> List[str]:
    r"""
    Create a list of requirements for a given package.

    Parameters
    ----------
    package : str
        The name of the package to create the requirements for.
    extras : list, optional
        A list of extras, install requirements to include in the requirements.
    fail : Fail, optional
        If an error is raised when the exact version is not found on PyPi. If False,
        a warning will be issued and the lowest available version will be returned.
        Default is False.

    Returns
    -------
    A list of requirements strings pinning at minimum requirement for the given package.

    Example
    -------
    No extras specified:
    >>> create("minimum_dependencies")
    ['importlib-metadata==4.11.4\n', 'packaging==23.0\n', 'requests==2.25.0\n']

    Extras specified:
    >>> create("minimum_dependencies", extras=["test", "testing_other"])
    ['importlib-metadata==4.11.4\n', 'packaging==23.0\n', 'requests==2.25.0\n',
    'pytest==6.0.0\n', 'pytest-doctestplus==0.12.0\n', 'astropy[all]==5.0\n',
    'numpy==1.20.0\n', 'scipy==1.6.0\n']
    """
    extras = [] if extras is None else extras
    requirements = []

    requires_ = requires(package)
    if requires_ is not None:
        for r in requires_:
            requirement = Requirement(r)

            if requirement.marker is None or any(
                requirement.marker.evaluate({"extra": e}) for e in extras
            ):
                name = (
                    f"{requirement.name}[{','.join(requirement.extras)}]"
                    if requirement.extras
                    else requirement.name
                )

                if requirement.url is None:
                    requirements.append(
                        f"{name}=={minimum_version(requirement, fail=fail)}\n",
                    )
                else:
                    requirements.append(f"{name} @{requirement.url}\n")

    return requirements


def write(
    package: str,
    filename: str = None,
    extras: list = None,
    fail: Fail = Fail.FALSE,
) -> None:
    """
    Write out a requirements file for a given package.

    Parameters
    ----------
    package : str
        The name of the package to create the requirements for.
    filename : str, optional
        The name of the file to write the requirements to.
        If not given, write to stdout.
    extras : list, optional
        A list of extras, install requirements to include in the requirements.
    error : Error, optional
        If an error is raised when the exact version is not found on PyPi. If False,
        a warning will be issued and the lowest available version will be returned.
        Default is False.

    Returns
    -------
    Nothing
    """
    requirements = "".join(create(package, extras=extras, fail=fail))

    if filename is None:
        sys.stdout.write(requirements)
        sys.stdout.flush()
    else:
        with Path(filename).open("w") as fd:
            fd.write(requirements)
