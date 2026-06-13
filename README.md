# AI Answer Evaluator

A small FastAPI and CLI tool that compares AI model answers with reference
answers using local, deterministic scoring. It makes no external API or LLM
calls and requires no environment variables.

## What This Does

Send a JSON list of evaluation items to `POST /evaluate`, or pass the same JSON
to the CLI. For each item, the evaluator returns:

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
├── app/
│   ├── main.py          # FastAPI routes
│   ├── cli.py           # File/stdin JSON interface
│   ├── models.py        # Request and response schemas
│   ├── scoring.py       # Pure normalization and scoring logic
│   └── service.py       # Batch evaluation and summary calculation
├── tests/
│   ├── test_api.py
│   ├── test_cli.py
│   ├── test_environment.py
│   ├── test_scoring.py
│   └── test_service.py
├── docs/
│   └── IMPLEMENTATION_GUIDE.md
├── .env.example         # Documents that no environment is required
├── main.py              # CLI entry point and FastAPI app export
├── sample_input.json
├── requirements.txt
└── requirements-dev.txt
```

## Run Locally

Python 3.11 or newer is recommended.

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate    # Windows: .venv\Scripts\activate
   ```

2. Install runtime and test dependencies:

   ```bash
   python -m pip install -r requirements-dev.txt
   ```

   No `.env` file or API key is needed.

3. Run the tests:

   ```bash
   pytest
   ```

## Run as a CLI

Read the sample from standard input:

```bash
python main.py < sample_input.json
```

Or pass the input file directly:

```bash
python main.py sample_input.json
```

Both commands print the complete JSON result to standard output. Invalid JSON
or invalid item structure is written to standard error with exit code `2`.

## Run as an API

1. Start the API:

   ```bash
   uvicorn main:app --reload
   ```

2. In another terminal, evaluate the sample data:

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

## Example Output

The included `sample_input.json` produces:

```json
{
  "results": [
    {"id": "1", "score": 0.4,  "reason": "Partial token overlap: 1 shared token(s) across 1 reference and 4 model token(s)."},
    {"id": "2", "score": 0.0,  "reason": "No shared tokens after normalization."},
    {"id": "3", "score": 0.4,  "reason": "Partial token overlap: 1 shared token(s) across 1 reference and 4 model token(s)."},
    {"id": "4", "score": 1.0,  "reason": "Exact match after normalization."}
  ],
  "summary": {
    "average_score": 0.45,
    "number_of_items": 4,
    "exact_matches": 1,
    "failed_items": 1
  }
}
```

## Edge Cases

- Missing, null, or whitespace-only answers receive `0.0`.
- Answers with no shared word tokens receive `0.0`.
- An empty input list returns an empty result list and a zeroed summary.
- Structurally invalid items, such as an item without `id`, return HTTP `422`.
- Punctuation is ignored during partial token comparison.

## Architecture Decisions

**Why `app/` is a package, not a single file**
Each layer has one responsibility: `scoring.py` is pure logic with no HTTP
imports, `service.py` owns batch aggregation, `main.py` owns routing. Another
engineer can swap the scoring algorithm without touching the API contract, or
test scoring logic without spinning up an HTTP client.

**Why token-set F1, not Jaccard**
F1 balances coverage of the reference against penalizing extra words in the
model answer. Jaccard divides by the union, which can over-penalize a model
that restates a short reference inside a longer sentence. F1 treats both sides
symmetrically and gives a more intuitive partial-credit signal for factual
answers.

**Why `PARTIAL_SCORE_CAP = 0.99`**
Partial scores are capped below `1.0` so that `score == 1.0` unambiguously
means an exact normalized match. Without the cap, a degenerate case (e.g.,
both answers are identical after tokenization but differ in punctuation) could
round to `1.0` without being a true exact match.

**Why Pydantic models on request and response**
FastAPI returns a `422` with a clear error body if the caller sends a
structurally invalid item (e.g., a missing `id`). This distinguishes API-level
errors (bad structure) from evaluation-level edge cases (missing answer
content), which score `0.0` rather than rejecting the request.

**Why the API and CLI share a service layer**
Both interfaces validate the same `EvaluationItem` model and call
`evaluate_items`. This prevents scoring behavior from drifting between API and
CLI usage while keeping input/output concerns separate.

## Tradeoffs and Known Limitations

| Limitation | Impact | Fix |
|---|---|---|
| Token overlap ignores word order | "cat bites dog" and "dog bites cat" score identically | Add n-gram or sequence similarity |
| No semantic similarity | "automobile" vs "car" scores `0.0` | Plug in a local sentence-transformer behind a scorer interface |
| Single reference answer per item | Aliases and paraphrases always score as partial | Accept a list of acceptable reference answers |
| In-memory only | No persistence, no audit log | Add SQLite backend with `GET /results/{run_id}` |
| No authentication or rate limiting | Open to abuse in a shared environment | Add API key middleware |

## What I'd Add Next

In priority order:

1. **Configurable scoring strategy** — accept `"strategy": "exact_only" | "token_f1" | "semantic"` per request behind a `ScorerStrategy` interface so callers can choose the right tradeoff.
2. **Semantic scorer** — plug in a local `sentence-transformers` model (e.g., `all-MiniLM-L6-v2`) as an optional strategy; no external API required.
3. **Multiple reference answers** — accept a list so synonyms and valid paraphrases are not unfairly penalized.
4. **Batch file ingestion** — `POST /evaluate/file` accepting a JSONL upload for offline batch jobs.
5. **Result persistence** — store evaluation runs in SQLite and expose `GET /results/{run_id}` for historical comparison.
6. **CI** — run the test suite on every push; add a coverage threshold gate.

See [docs/IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md) for the full
step-by-step design and explanation guide.

## About the Developer

Built by **Aishwarya Anand** — [github.com/aish-1509](https://github.com/aish-1509)

Relevant background:
- Built and deployed a **local LLM chatbot using Ollama** at Panasonic (production setting, internal tooling)
- Evaluated **multi-agent AI workflows** (Wan 2.2, SlimInfer, CODI) for enterprise adoption
- FastAPI and REST API development across multiple internship engagements
