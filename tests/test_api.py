import asyncio
import json
from pathlib import Path

import httpx

from app.main import app


def get(path: str) -> httpx.Response:
    """Send a GET request directly to the ASGI app."""

    async def send_request() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.get(path)

    return asyncio.run(send_request())


def post(path: str, json_body: object) -> httpx.Response:
    """Send a request directly to the ASGI app without opening a network port."""

    async def send_request() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.post(path, json=json_body)

    return asyncio.run(send_request())


def test_root_explains_how_to_use_the_api() -> None:
    response = get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "AI Answer Evaluator",
        "status": "ready",
        "evaluate": "POST /evaluate",
        "documentation": "/docs",
        "health": "/health",
    }


def test_favicon_request_does_not_return_not_found() -> None:
    response = get("/favicon.ico")

    assert response.status_code == 204


def test_evaluate_endpoint_with_sample_input() -> None:
    sample_path = Path(__file__).parent.parent / "sample_input.json"
    items = json.loads(sample_path.read_text(encoding="utf-8"))

    response = post("/evaluate", items)

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == {
        "average_score": 0.45,
        "number_of_items": 4,
        "exact_matches": 1,
        "failed_items": 1,
    }
    assert [item["id"] for item in body["results"]] == ["1", "2", "3", "4"]


def test_missing_answer_is_scored_instead_of_rejected() -> None:
    response = post(
        "/evaluate",
        [
            {
                "id": "missing-model-answer",
                "prompt": "Give an answer.",
                "reference_answer": "expected",
            }
        ],
    )

    assert response.status_code == 200
    assert response.json()["results"][0] == {
        "id": "missing-model-answer",
        "score": 0.0,
        "reason": "Model answer is missing.",
    }


def test_invalid_item_without_id_returns_validation_error() -> None:
    response = post(
        "/evaluate",
        [
            {
                "prompt": "Give an answer.",
                "reference_answer": "expected",
                "model_answer": "expected",
            }
        ],
    )

    assert response.status_code == 422
