"""Core functionality for minimum_dependencies."""

import sys
import warnings
from contextlib import suppress
from pathlib import Path

import requests
from importlib_metadata import requires
from packaging.requirements import Requirement
from packaging.version import InvalidVersion, Version, parse


def versions(requirement: Requirement) -> list[Version]:
    """Get the versions available on PyPi for a given requirement."""
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


def minimum_version(requirement: Requirement) -> Version:
    """Return minimum version available on PyPi for a given version specification."""
    if not requirement.specifier:
        warnings.warn(
            f"No version specifier for {requirement.name} in install_requires.\n"
            "Using lowest available version on PyPi.",
            stacklevel=2,
        )

    for version in (versions_ := versions(requirement)):
        if version in requirement.specifier:
            # If the requirement does not list any version, the lowest will be
            return version

    # If the specified version does not exist on PyPi, issue a warning
    # and return the lowest available version
    warnings.warn(
        f"Exact version specified in {requirement} not found on PyPi.\n"
        "Using lowest available version.",
        stacklevel=2,
    )
    return versions_[0]


def create(package: str, extras: list = None) -> list[str]:
    """Create a list of requirements for a given package."""
    extras = [] if extras is None else extras

    requirements = []
    for r in requires(package):
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
                    f"{name}=={minimum_version(requirement)}\n",
                )
            else:
                requirements.append(f"{name} @{requirement.url}\n")

    return requirements


def write(package: str, filename: str = None, extras: list = None) -> None:
    """Write out a requirements file for a given package."""
    requirements = "".join(create(package, extras=extras))

    if filename is None:
        sys.stdout.write(requirements)
        sys.stdout.flush()
    else:
        with Path(filename).open("w") as fd:
            fd.write(requirements)
