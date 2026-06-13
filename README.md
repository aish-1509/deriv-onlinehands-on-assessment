# AI Answer Evaluator

A small FastAPI service that compares AI model answers with reference answers
using local, deterministic scoring. It makes no external API or LLM calls.

## What This Does

Send a JSON list of evaluation items to `POST /evaluate`. For each item, the
service returns:

- the original `id`
- a score from `0.0` to `1.0`
- a short explanation

It also returns the average score, item count, exact-match count, and failed
item count.

## Scoring Rules

1. Lowercase each answer and trim surrounding whitespace.
2. Return `0.0` if either normalized answer is empty.
3. Return `1.0` if the normalized answers are identical.
4. Otherwise, extract unique word tokens and calculate token-set F1:

   ```text
   partial score = 2 * shared tokens / (reference tokens + model tokens)
   ```

5. Cap partial scores at `0.99`, so only an exact normalized match receives
   `1.0`.
6. Round scores and the batch average to four decimal places.

This makes scoring repeatable and easy to explain. It does not attempt to
measure semantic equivalence.

## Project Structure

```text
.
|-- app/
|   |-- main.py          # FastAPI routes
|   |-- models.py        # Request and response schemas
|   |-- scoring.py       # Pure normalization and scoring logic
|   `-- service.py       # Batch evaluation and summary calculation
|-- tests/
|   |-- test_api.py
|   |-- test_scoring.py
|   `-- test_service.py
|-- docs/
|   `-- IMPLEMENTATION_GUIDE.md
|-- main.py              # Simple uvicorn entry point
|-- sample_input.json
|-- requirements.txt
`-- requirements-dev.txt
```

## Run Locally

Python 3.11 or newer is recommended.

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install runtime and test dependencies:

   ```bash
   python -m pip install -r requirements-dev.txt
   ```

3. Run the tests:

   ```bash
   pytest
   ```

4. Start the API:

   ```bash
   uvicorn main:app --reload
   ```

5. In another terminal, evaluate the sample data:

   ```bash
   curl --silent \
     --request POST \
     --header "Content-Type: application/json" \
     --data @sample_input.json \
     http://127.0.0.1:8000/evaluate | python -m json.tool
   ```

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Example Summary

The included sample produces:

```json
{
  "average_score": 0.45,
  "number_of_items": 4,
  "exact_matches": 1,
  "failed_items": 1
}
```

## Edge Cases

- Missing, null, or whitespace-only answers receive `0.0`.
- Answers with no shared word tokens receive `0.0`.
- An empty input list returns an empty result list and a zeroed summary.
- Structurally invalid items, such as an item without `id`, return HTTP `422`.
- Punctuation is ignored for partial token comparison.

## Tradeoffs and Next Improvements

The token score is transparent and fast, but it cannot understand synonyms,
facts expressed with different wording, negation, or answer correctness beyond
the provided reference. A production version could add configurable scoring
strategies, per-item weights, pass thresholds, duplicate-ID validation, batch
size limits, persistence, authentication, and observability.

See [docs/IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md) for the full
step-by-step design and explanation guide.
