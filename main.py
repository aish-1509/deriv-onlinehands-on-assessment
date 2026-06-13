"""Run the evaluator as an API or CLI from one convenient entry point."""

import argparse
import sys
from pathlib import Path
from typing import Sequence

import uvicorn

from app.cli import run_cli
from app.main import app


def build_parser() -> argparse.ArgumentParser:
    """Create command-line options for API and CLI usage."""
    parser = argparse.ArgumentParser(
        description=(
            "Start the API in an interactive terminal, or evaluate JSON from "
            "a file or standard input."
        )
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        type=Path,
        help="JSON input file. Piped JSON is read from standard input.",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API host when no CLI input is provided (default: 0.0.0.0).",
    )
    parser.add_argument(
        "--port",
        default=8000,
        type=int,
        help="API port when no CLI input is provided (default: 8000).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Select CLI mode for JSON input; otherwise start the API server."""
    args = build_parser().parse_args(argv)

    if args.input_file is not None or not sys.stdin.isatty():
        return run_cli(args.input_file)

    uvicorn.run("main:app", host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
