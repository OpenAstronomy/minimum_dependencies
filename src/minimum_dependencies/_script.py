"""Contain the function linked to by the entry point."""

from pathlib import Path

import typer

from minimum_dependencies._core import write


def minimum_dependencies(
    package: str = typer.Argument(
        ..., help="Name of the package to generate requirements for"
    ),
    filename: Path = typer.Option(
        None, "--filename", "-f", help="Name of the file to write out"
    ),
    extras: str = typer.Option(
        None,
        "--extras",
        "-e",
        help="Comma-separated list of optional dependency sets to include",
    ),
):
    """Generate the minimum requirements for a package based on the lower pins of its dependencies."""
    if extras is not None:
        extras = extras.split(",")
    write(package, filename, extras)


def main():
    typer.run(minimum_dependencies)
