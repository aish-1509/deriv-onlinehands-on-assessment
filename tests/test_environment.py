from pathlib import Path

from app.models import EvaluationItem
from app.service import evaluate_items

PROJECT_ROOT = Path(__file__).parent.parent


def test_no_local_env_file_or_configuration_is_required() -> None:
    assert not (PROJECT_ROOT / ".env").exists()
    assert (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8") == (
        "# No environment variables are required.\n"
    )

    result = evaluate_items(
        [
            EvaluationItem(
                id="local",
                prompt="Reply with yes.",
                reference_answer="yes",
                model_answer="YES",
            )
        ]
    )

    assert result.results[0].score == 1.0
