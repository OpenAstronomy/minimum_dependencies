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

app = typer.Typer()


@app.command()
def minimum_dependencies(
    package: str = __PACKAGE_ARGUMENT,
    filename: Path = __FILENAME_OPTION,
    extras: List[str] = __EXTRAS_OPTION,
) -> None:
    """Generate minimum requirements for a package based on lower dependency pins."""
    if extras is not None and len(extras) == 1:
        extras = extras[0].split(",")
    write(package, filename, extras)


def main() -> None:
    app()
