"""Typed request and response models for the evaluation API."""

from pydantic import BaseModel, Field


class EvaluationItem(BaseModel):
    """One prompt, expected answer, and model answer to evaluate."""

    id: str = Field(min_length=1, description="Caller-provided item identifier.")
    prompt: str = Field(min_length=1, description="Prompt shown to the model.")
    reference_answer: str | None = Field(
        default=None,
        description="Expected answer. Null or blank values receive a zero score.",
    )
    model_answer: str | None = Field(
        default=None,
        description="Answer produced by the model. Null or blank values receive zero.",
    )


class ItemResult(BaseModel):
    """Score and explanation for one evaluation item."""

    id: str
    score: float = Field(ge=0.0, le=1.0)
    reason: str


class EvaluationSummary(BaseModel):
    """Aggregate statistics for an evaluation batch."""

    average_score: float = Field(ge=0.0, le=1.0)
    number_of_items: int = Field(ge=0)
    exact_matches: int = Field(ge=0)
    failed_items: int = Field(ge=0)


class EvaluationResponse(BaseModel):
    """Complete response returned by the evaluation endpoint."""

    results: list[ItemResult]
    summary: EvaluationSummary
