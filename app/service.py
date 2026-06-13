"""Application service for evaluating a batch and calculating its summary."""

from app.models import (
    EvaluationItem,
    EvaluationResponse,
    EvaluationSummary,
    ItemResult,
)
from app.scoring import score_answers


def evaluate_items(items: list[EvaluationItem]) -> EvaluationResponse:
    """Evaluate every item and aggregate deterministic batch statistics."""
    results: list[ItemResult] = []
    exact_matches = 0
    failed_items = 0

    for item in items:
        outcome = score_answers(item.reference_answer, item.model_answer)
        results.append(
            ItemResult(
                id=item.id,
                score=outcome.score,
                reason=outcome.reason,
            )
        )
        exact_matches += int(outcome.is_exact)
        failed_items += int(outcome.score == 0.0)

    average_score = (
        round(sum(result.score for result in results) / len(results), 4)
        if results
        else 0.0
    )

    return EvaluationResponse(
        results=results,
        summary=EvaluationSummary(
            average_score=average_score,
            number_of_items=len(results),
            exact_matches=exact_matches,
            failed_items=failed_items,
        ),
    )
