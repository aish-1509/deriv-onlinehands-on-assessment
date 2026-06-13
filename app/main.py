"""FastAPI application and HTTP endpoints."""

from fastapi import FastAPI, Response

from app.models import EvaluationItem, EvaluationResponse
from app.service import evaluate_items

app = FastAPI(
    title="AI Answer Evaluator",
    description="Deterministically compare model answers with reference answers.",
    version="1.0.0",
)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    """Describe the service and point browser users to its documentation."""
    return {
        "name": "AI Answer Evaluator",
        "status": "ready",
        "evaluate": "POST /evaluate",
        "documentation": "/docs",
        "health": "/health",
    }


@app.get("/favicon.ico", include_in_schema=False, status_code=204)
def favicon() -> Response:
    """Avoid a browser favicon 404 for this API-only project."""
    return Response(status_code=204)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Return a simple readiness response."""
    return {"status": "healthy"}


@app.post("/evaluate", response_model=EvaluationResponse, tags=["evaluation"])
def evaluate(items: list[EvaluationItem]) -> EvaluationResponse:
    """Score a list of model answers and return item-level and summary results."""
    return evaluate_items(items)
