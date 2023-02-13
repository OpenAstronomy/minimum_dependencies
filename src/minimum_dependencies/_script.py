"""Contain the function linked to by the entry point."""

from pathlib import Path  # noqa: TCH003
from typing import List

import typer

from minimum_dependencies._core import write

__PACKAGE_ARGUMENT = typer.Argument(
    ...,
    help="Name of the package to generate requirements for",
)
__FILENAME_OPTION = typer.Option(
    None,
    "--filename",
    "-f",
    help="Name of the file to write out",
)
__EXTRAS_OPTION = typer.Option(
    None,
    "--extras",
    "-e",
    help="Comma-separated list of optional dependency sets to include",
)
__FAIL_OPTION = typer.Option(
    False,  # noqa: FBT003
    "--fail",
    help="Raise an error if pin is not present or not on PyPi.",
)

app = typer.Typer(add_completion=False)


@app.command()
def minimum_dependencies(
    package: str = __PACKAGE_ARGUMENT,
    filename: Path = __FILENAME_OPTION,
    extras: List[str] = __EXTRAS_OPTION,
    fail: bool = __FAIL_OPTION,  # noqa: FBT001
) -> None:
    """Generate minimum requirements for a package based on lower dependency pins."""
    if extras is not None and len(extras) == 1:
        extras = extras[0].split(",")
    write(package=package, filename=filename, extras=extras, fail=fail)


def main() -> None:
    app()
