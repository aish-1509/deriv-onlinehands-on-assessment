"""FastAPI application and HTTP endpoints."""

from fastapi import FastAPI

from app.models import EvaluationItem, EvaluationResponse
from app.service import evaluate_items

app = FastAPI(
    title="AI Answer Evaluator",
    description="Deterministically compare model answers with reference answers.",
    version="1.0.0",
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Return a simple readiness response."""
    return {"status": "healthy"}


@app.post("/evaluate", response_model=EvaluationResponse, tags=["evaluation"])
def evaluate(items: list[EvaluationItem]) -> EvaluationResponse:
    """Score a list of model answers and return item-level and summary results."""
    return evaluate_items(items)
