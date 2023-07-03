"""Contain the function linked to by the entry point."""


from argparse import ArgumentParser
from itertools import chain
from typing import Optional

from ._core import write


def _argparser() -> ArgumentParser:
    """Create the argument parser."""
    parser = ArgumentParser(
        "minimum_deps",
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


def main(args: Optional[any] = None) -> None:
    """Run the script."""
    parser = _argparser()
    args = parser.parse_args(args)
    extras = None if args.extras is None else list(chain.from_iterable(args.extras))

    write(args.package[0], filename=args.filename, extras=extras, fail=args.fail)
