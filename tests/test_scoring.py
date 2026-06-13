import pytest

from app.scoring import PARTIAL_SCORE_CAP, normalize_text, score_answers


def test_normalization_and_exact_match() -> None:
    assert normalize_text("  Approved \n") == "approved"

    result = score_answers("approved", "  Approved ")

    assert result.score == 1.0
    assert result.is_exact is True
    assert result.reason == "Exact match after normalization."


def test_normalization_does_not_hide_punctuation_differences() -> None:
    assert normalize_text(" Approved. ") == "approved."

    result = score_answers("approved", "approved.")

    assert result.score == PARTIAL_SCORE_CAP
    assert result.is_exact is False


def test_partial_score_uses_token_f1_overlap() -> None:
    result = score_answers("Earth", "Humans live on Earth.")

    assert result.score == pytest.approx(0.4)
    assert result.is_exact is False
    assert result.reason.startswith("Partial token overlap")


@pytest.mark.parametrize(
    ("reference", "model", "expected_reason"),
    [
        (None, "answer", "Reference answer is missing."),
        ("answer", "   ", "Model answer is missing."),
        (None, None, "Reference and model answers are missing."),
        ("red", "blue", "No shared tokens after normalization."),
    ],
)
def test_zero_score_edge_cases(
    reference: str | None,
    model: str | None,
    expected_reason: str,
) -> None:
    result = score_answers(reference, model)

    assert result.score == 0.0
    assert result.reason == expected_reason


def test_partial_score_never_reaches_exact_match_threshold() -> None:
    result = score_answers("yes", "yes please confirm")

    assert result.score <= PARTIAL_SCORE_CAP
    assert result.is_exact is False
