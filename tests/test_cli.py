import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SAMPLE_INPUT = PROJECT_ROOT / "sample_input.json"


def test_cli_reads_json_from_standard_input() -> None:
    completed = subprocess.run(
        [sys.executable, "main.py"],
        cwd=PROJECT_ROOT,
        input=SAMPLE_INPUT.read_text(encoding="utf-8"),
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stderr == ""
    output = json.loads(completed.stdout)
    assert output["summary"] == {
        "average_score": 0.45,
        "number_of_items": 4,
        "exact_matches": 1,
        "failed_items": 1,
    }


def test_cli_accepts_an_input_file() -> None:
    completed = subprocess.run(
        [sys.executable, "main.py", str(SAMPLE_INPUT)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert json.loads(completed.stdout)["results"][3]["score"] == 1.0


def test_cli_reports_invalid_json_cleanly() -> None:
    completed = subprocess.run(
        [sys.executable, "main.py"],
        cwd=PROJECT_ROOT,
        input="{not valid json",
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 2
    assert completed.stdout == ""
    assert completed.stderr.startswith("Input error:")


def test_help_does_not_attempt_to_read_json() -> None:
    completed = subprocess.run(
        [sys.executable, "main.py", "--help"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "Start the API in an interactive terminal" in completed.stdout
    assert completed.stderr == ""
