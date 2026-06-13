# AI Answer Evaluator

[![CI](https://github.com/aish-1509/deriv-onlinehands-on-assessment/actions/workflows/ci.yml/badge.svg)](https://github.com/aish-1509/deriv-onlinehands-on-assessment/actions/workflows/ci.yml)

A local Python tool that compares AI model answers with reference answers using
simple, deterministic rules. It supports both FastAPI and CLI usage and makes
no external API or LLM calls.

## Requirements Coverage

| Requirement | Implementation |
| --- | --- |
| Accept a list of evaluation items | JSON list through `POST /evaluate`, stdin, or a file |
| Normalize answers | Lowercase and trim surrounding whitespace |
| Exact score | `1.0` for equal normalized answers |
| Partial score | Token-set F1 overlap for non-exact answers |
| Missing answer | `0.0` with a short reason |
| Per-item output | `id`, `score`, and `reason` |
| Summary | Average, item count, exact matches, and failed items |
| Local only | No external services or environment variables |

## Project Structure

```text
app/
  cli.py       JSON file/stdin interface
  main.py      FastAPI routes
  models.py    Request and response models
  scoring.py   Pure deterministic scoring
  service.py   Batch evaluation and summary
tests/         Unit, API, CLI, and edge-case tests
docs/          Design and extension notes
main.py        API/CLI entry point
sample_input.json
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
pytest
```

No `.env` file or API key is required.

## Run the API

```bash
python main.py
```

Open:

- Service information: http://127.0.0.1:8000/
- Interactive API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

Evaluate the sample:

```bash
curl --silent \
  --request POST \
  --header "Content-Type: application/json" \
  --data @sample_input.json \
  http://127.0.0.1:8000/evaluate | python -m json.tool
```

## Run the CLI

From stdin:

```bash
python main.py < sample_input.json
```

From a file:

```bash
python main.py sample_input.json
```

Invalid JSON or invalid item structure is written to stderr with exit code `2`.

## Scoring

1. Convert each answer to lowercase and trim surrounding whitespace.
2. Return `0.0` when either normalized answer is empty.
3. Return `1.0` when normalized answers match exactly.
4. Otherwise, extract unique word tokens and calculate:

   ```text
   token F1 = 2 * shared_token_count
              / (reference_token_count + model_token_count)
   ```

5. Cap partial scores at `0.99`, keeping `1.0` reserved for exact matches.
6. Round item scores and the average to four decimal places.

The included sample returns scores `[0.4, 0.0, 0.4, 1.0]` and:

```json
{
  "average_score": 0.45,
  "number_of_items": 4,
  "exact_matches": 1,
  "failed_items": 1
}
```

## Edge Cases

- Missing, null, or whitespace-only answers score `0.0`.
- Answers with no shared tokens score `0.0`.
- An empty list returns an empty result list and a zeroed summary.
- Structurally invalid items return HTTP `422` or CLI exit code `2`.
- Punctuation is ignored during partial tokenization, but not exact matching.

## Manual Checks

```bash
# Sample batch
python main.py sample_input.json

# Missing model answer
printf '%s\n' \
  '[{"id":"missing","prompt":"Test","reference_answer":"yes"}]' \
  | python main.py

# Invalid JSON: prints an error and exits with code 2
printf '{invalid' | python main.py
```

## Tradeoffs and Next Steps

Token overlap is transparent and fast, but it does not understand synonyms,
negation, word order, or semantic equivalence. Logical extensions are multiple
acceptable references, configurable scoring strategies, batch-size limits,
result persistence, and observability.

See [docs/IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md) for the design
walkthrough.
