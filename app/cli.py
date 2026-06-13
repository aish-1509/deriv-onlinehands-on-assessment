"""Command-line interface for local JSON evaluation."""

import json
import sys
from pathlib import Path
from typing import TextIO

from pydantic import TypeAdapter, ValidationError

from app.models import EvaluationItem
from app.service import evaluate_items

ITEM_LIST_ADAPTER = TypeAdapter(list[EvaluationItem])


def read_items(input_file: Path | None, stdin: TextIO) -> list[EvaluationItem]:
    """Read and validate evaluation items from a file or standard input."""
    if input_file is None:
        payload = json.load(stdin)
    else:
        with input_file.open(encoding="utf-8") as file:
            payload = json.load(file)

    return ITEM_LIST_ADAPTER.validate_python(payload)


def run_cli(
    input_file: Path | None = None,
    *,
    stdin: TextIO = sys.stdin,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    """Evaluate JSON input, write JSON output, and return a process exit code."""
    try:
        items = read_items(input_file, stdin)
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        print(f"Input error: {error}", file=stderr)
        return 2

    response = evaluate_items(items)
    json.dump(response.model_dump(mode="json"), stdout, indent=2)
    stdout.write("\n")
    return 0
