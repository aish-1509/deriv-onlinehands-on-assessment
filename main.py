"""CLI entry point and FastAPI application export."""

import argparse
import sys
from pathlib import Path
from typing import Sequence

from app.cli import run_cli
from app.main import app


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate AI answers from a JSON file or standard input. "
            "Use `uvicorn main:app --reload` to run the API."
        )
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        type=Path,
        help="JSON input file. Omit this argument to read JSON from standard input.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the local JSON evaluation CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.input_file is None and sys.stdin.isatty():
        parser.error("provide an input file or pipe JSON to standard input")

    return run_cli(args.input_file)


if __name__ == "__main__":
    raise SystemExit(main())
