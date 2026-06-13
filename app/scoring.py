"""Pure, deterministic text normalization and scoring functions."""

import re
from dataclasses import dataclass

TOKEN_PATTERN = re.compile(r"\w+", flags=re.UNICODE)
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "in",
    "is",
    "it",
    "of",
    "the",
    "to",
    "was",
    "were",
}
PARTIAL_SCORE_CAP = 0.99


@dataclass(frozen=True)
class ScoreResult:
    """Internal score details used to build the public API response."""

    score: float
    reason: str
    is_exact: bool = False


def normalize_text(text: str | None) -> str:
    """Lowercase text and trim leading and trailing whitespace."""
    if text is None:
        return ""
    return text.strip().lower()


def tokenize(text: str) -> set[str]:
    """Return unique tokens, ignoring punctuation and common stopwords."""
    tokens = set(TOKEN_PATTERN.findall(text))
    filtered = tokens - STOPWORDS
    return filtered if filtered else tokens


def score_answers(
    reference_answer: str | None,
    model_answer: str | None,
) -> ScoreResult:
    """Compare two answers using exact match, then token-set F1 overlap."""
    reference = normalize_text(reference_answer)
    model = normalize_text(model_answer)

    if not reference and not model:
        return ScoreResult(
            score=0.0,
            reason="Reference and model answers are missing.",
        )
    if not reference:
        return ScoreResult(score=0.0, reason="Reference answer is missing.")
    if not model:
        return ScoreResult(score=0.0, reason="Model answer is missing.")

    if reference == model:
        return ScoreResult(
            score=1.0,
            reason="Exact match after normalization.",
            is_exact=True,
        )

    reference_tokens = tokenize(reference)
    model_tokens = tokenize(model)
    shared_tokens = reference_tokens & model_tokens

    if not reference_tokens or not model_tokens:
        return ScoreResult(
            score=0.0,
            reason="No comparable word tokens after normalization.",
        )
    if not shared_tokens:
        return ScoreResult(
            score=0.0,
            reason="No shared tokens after normalization.",
        )

    token_f1 = (2 * len(shared_tokens)) / (
        len(reference_tokens) + len(model_tokens)
    )
    score = round(min(token_f1, PARTIAL_SCORE_CAP), 4)
    reason = (
        f"Partial token overlap: {len(shared_tokens)} shared token(s) across "
        f"{len(reference_tokens)} reference and {len(model_tokens)} model token(s)."
    )
    return ScoreResult(score=score, reason=reason)
