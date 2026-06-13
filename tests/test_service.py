from app.models import EvaluationItem
from app.service import evaluate_items


def test_sample_batch_summary() -> None:
    items = [
        EvaluationItem(
            id="1",
            prompt="What is 2 + 2?",
            reference_answer="4",
            model_answer="The answer is 4.",
        ),
        EvaluationItem(
            id="2",
            prompt="Name one primary color.",
            reference_answer="red",
            model_answer="blue",
        ),
        EvaluationItem(
            id="3",
            prompt="What planet do humans live on?",
            reference_answer="Earth",
            model_answer="Humans live on Earth.",
        ),
        EvaluationItem(
            id="4",
            prompt="Reply with exactly: approved",
            reference_answer="approved",
            model_answer="Approved",
        ),
    ]

    response = evaluate_items(items)

    assert [result.score for result in response.results] == [0.6667, 0.0, 0.4, 1.0]
    assert response.summary.average_score == 0.5167
    assert response.summary.number_of_items == 4
    assert response.summary.exact_matches == 1
    assert response.summary.failed_items == 1


def test_empty_batch_has_zeroed_summary() -> None:
    response = evaluate_items([])

    assert response.results == []
    assert response.summary.average_score == 0.0
    assert response.summary.number_of_items == 0
    assert response.summary.exact_matches == 0
    assert response.summary.failed_items == 0
