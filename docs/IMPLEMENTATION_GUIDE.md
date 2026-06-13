# Implementation Guide

This guide explains the build order, code structure, reasoning, testing flow,
and a clean way to present the solution during an assessment.

## 1. Restate the Problem

The service receives a batch of prompts with reference answers and model
answers. It must produce deterministic per-item scores and aggregate summary
statistics without calling an LLM or any external service.

The important design constraint is determinism: the same input must always
produce the same output.

## 2. Choose the Smallest Useful Architecture

Use one evaluation service with two small interfaces, and separate input/output
concerns from scoring concerns:

```text
HTTP request                 JSON file or stdin
    |                              |
    v                              v
app/main.py                    app/cli.py
    |                              |
    +--------------+---------------+
                   |
                   v
app/service.py       Evaluate all items and aggregate statistics
                   |
                   v
app/scoring.py       Normalize and score one answer pair
                   |
                   v
app/models.py        Shape and validate the response
```

This is slightly more structured than putting everything in one file, but each
file has one clear responsibility. Another engineer can replace the scoring
algorithm without changing the API route.

## 3. Define the Data Contract First

`EvaluationItem` requires:

- `id`: required because every output must identify its source item
- `prompt`: required because it is part of the evaluation record
- `reference_answer`: optional so a missing answer can produce a scored result
- `model_answer`: optional for the same reason

The prompt is not used by the current scorer. The requested deterministic rule
compares the model answer with the reference answer. Keeping the prompt in the
schema preserves context and allows future prompt-aware scoring.

Invalid item structure is an API-level error. Missing answer content is a
scoring-level edge case. That distinction is why a missing `id` returns `422`,
while a missing `model_answer` returns a valid result with score `0.0`.

## 4. Normalize Before Comparing

`normalize_text` does exactly what the requirements specify:

1. Convert `None` to an empty string.
2. Trim leading and trailing whitespace.
3. Lowercase the text.

Examples:

```text
" Approved " -> "approved"
"EARTH"       -> "earth"
None          -> ""
```

Normalization is intentionally conservative. It does not rewrite grammar,
remove internal words, or guess meaning.

## 5. Score in a Clear Decision Order

`score_answers` follows this order:

1. If both answers are empty, return `0.0`.
2. If either individual answer is empty, return `0.0`.
3. If normalized strings match exactly, return `1.0`.
4. Tokenize both strings while ignoring punctuation and common stopwords.
5. If there are no comparable or shared tokens, return `0.0`.
6. Otherwise calculate token-set F1 and cap it at `0.99`.

Token-set F1 is:

```text
2 * number of shared tokens
--------------------------------------------
reference token count + model token count
```

For `"Earth"` and `"Humans live on Earth."`:

```text
reference tokens = {"earth"}
model tokens     = {"humans", "live", "on", "earth"}
shared tokens    = {"earth"}

score = 2 * 1 / (1 + 4) = 0.4
```

F1 is preferable to reference-only coverage here because it rewards finding
the expected words while also penalizing unrelated extra words. Using sets
keeps the rule simple and prevents repeated words from inflating the score.

## 6. Build the Batch Summary Separately

`evaluate_items` calls the pure scorer once per item and tracks:

- total score for the average
- exact matches using the scorer's explicit `is_exact` flag
- failures where score equals `0.0`
- total number of results

The empty-list case is handled without division by zero and returns:

```json
{
  "average_score": 0.0,
  "number_of_items": 0,
  "exact_matches": 0,
  "failed_items": 0
}
```

## 7. Keep Both Interfaces Thin

`app/main.py` contains no scoring math. It only:

1. Creates the FastAPI application.
2. Exposes browser guidance at `GET /` and readiness at `GET /health`.
3. Accepts `POST /evaluate`.
4. Delegates the batch to `evaluate_items`.

`app/cli.py` also contains no scoring math. It:

1. Reads JSON from a file or standard input.
2. Validates the same `EvaluationItem` model used by FastAPI.
3. Delegates the batch to `evaluate_items`.
4. Prints the typed response as JSON.

The root `main.py` exposes the FastAPI app and runs the CLI:

```bash
python main.py
python main.py < sample_input.json
python main.py sample_input.json
uvicorn main:app --reload
```

No `.env` file, API key, or external service is required.

## 8. Test by Responsibility

The tests are split for fast diagnosis:

- `test_scoring.py`: normalization, exact scoring, partial scoring, missing
  answers, and zero overlap
- `test_service.py`: summary arithmetic and empty batches
- `test_api.py`: HTTP response shape, missing answers, and schema validation
- `test_cli.py`: stdin, file input, JSON output, and invalid input behavior
- `test_entrypoint.py`: verifies `python main.py` selects API mode in a terminal
- `test_environment.py`: verifies the project runs without `.env` or API keys

Run everything with:

```bash
pytest
```

Then run a real request against the local server:

```bash
uvicorn main:app --reload
curl --silent --request POST \
  --header "Content-Type: application/json" \
  --data @sample_input.json \
  http://127.0.0.1:8000/evaluate | python -m json.tool
```

## 9. How to Explain the Solution

A concise walkthrough can sound like this:

1. "I chose FastAPI because the input and output are naturally structured JSON,
   and its schemas make validation visible."
2. "The route is deliberately thin. It delegates to a service, which delegates
   each answer pair to a pure scoring function."
3. "I first normalize and check exact equality. Only non-exact answers reach the
   token scorer."
4. "For partial credit I use token-set F1, which balances expected-token coverage
   against unrelated extra text."
5. "Missing answers return a normal zero-score result because that is an expected
   evaluation outcome. Missing IDs return `422` because the request itself is
   invalid."
6. "The tests cover the algorithm, aggregation, and HTTP contract independently."
7. "The CLI and API share the same service, so both interfaces produce the same
   scores without duplicated business logic."

## 10. Tradeoffs

The current design favors transparency over linguistic sophistication.

- It cannot recognize synonyms such as `"automobile"` and `"car"`.
- It does not detect contradictions or negation.
- Token order and repeated-token frequency are ignored.
- The score is tied to one reference answer.
- Results are calculated in memory and are not persisted.

These are acceptable tradeoffs for a lightweight pre-release evaluation tool
whose rules must be deterministic and explainable.

## 11. Logical Extension Order

If more time becomes available, extend in this order:

1. Add configurable scoring strategies behind a shared scorer interface.
2. Add pass thresholds and per-item weights.
3. Add duplicate-ID checks and maximum batch sizes.
4. Support multiple acceptable reference answers.
5. Add persistence for evaluation runs and historical comparison.
6. Add authentication, rate limits, structured logging, and metrics.
7. Add CI to run the test suite on every push.

This order improves product usefulness before adding operational complexity.
