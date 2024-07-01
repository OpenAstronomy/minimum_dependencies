"""Contain the function linked to by the entry point."""

from __future__ import annotations

from argparse import ArgumentParser
from itertools import chain

from ._core import write


def _argparser() -> ArgumentParser:
    """Create the argument parser."""
    parser = ArgumentParser(
        "minimum_dependencies",
        description=(
            "Generate the minimum requirements for a package based on "
            "the lower pins of its dependencies."
        ),
    )
    parser.add_argument(
        "package",
        type=str,
        nargs=1,
        help="Name of the package to generate requirements for",
    )
    parser.add_argument(
        "--filename",
        "-f",
        default=None,
        help="Name of the file to write out",
    )
    parser.add_argument(
        "--extras",
        "-e",
        nargs="*",
        default=None,
        action="append",
        help="List of optional dependency sets to include",
    )
    parser.add_argument(
        "--fail",
        action="store_true",
        default=False,
        help="Raise an error if pin is not present or not on PyPi.",
    )
    return parser


def main(args: list[str] | None = None) -> None:
    """Run the script."""
    parser = _argparser()
    parsed_args = parser.parse_args(args)
    extras = (
        None
        if parsed_args.extras is None
        else list(chain.from_iterable(parsed_args.extras))
    )

    write(
        parsed_args.package[0],
        filename=parsed_args.filename,
        extras=extras,
        fail=parsed_args.fail,
    )
