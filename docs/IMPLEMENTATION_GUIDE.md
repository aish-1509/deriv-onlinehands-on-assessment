# Implementation Guide

## Design

The project keeps input/output concerns separate from scoring:

```text
FastAPI request        JSON file or stdin
      |                       |
      v                       v
 app/main.py              app/cli.py
      |                       |
      +----------+------------+
                 |
                 v
          app/service.py
                 |
                 v
          app/scoring.py
```

- `models.py` defines the shared request and response contract.
- `scoring.py` contains pure functions with no HTTP or file-system dependencies.
- `service.py` evaluates a batch and calculates summary statistics.
- The API and CLI call the same service, preventing behavior drift.

## Scoring Decision Order

For each item:

1. Lowercase and trim both answers.
2. Return `0.0` if either answer is empty.
3. Return `1.0` for an exact normalized match.
4. Extract unique word tokens, ignoring punctuation.
5. Return `0.0` if no tokens overlap.
6. Calculate token-set F1 and cap it at `0.99`.

Example:

```text
reference: "Earth"                 -> {"earth"}
model:     "Humans live on Earth." -> {"humans", "live", "on", "earth"}

score = 2 * 1 / (1 + 4) = 0.4
```

The cap keeps `score == 1.0` synonymous with an exact normalized match.

## Validation Choices

- `id` and `prompt` are required because they identify the evaluation record.
- Answer fields are nullable because a missing answer is an expected evaluation
  result, not a malformed request.
- FastAPI returns `422` for invalid structure.
- The CLI returns exit code `2` for invalid JSON or invalid structure.
- Empty batches return a zeroed summary without division by zero.

## Testing

```bash
pytest
```

The suite covers:

- normalization, exact scoring, partial scoring, and missing answers
- batch averages, exact counts, failure counts, and empty batches
- FastAPI routes and validation
- CLI stdin, file input, help, and invalid JSON
- API/CLI entry-point selection
- the absence of required environment configuration

GitHub Actions runs the same suite on pushes and pull requests.

## Extension Points

The first useful additions would be:

1. Multiple acceptable reference answers.
2. Configurable exact-only or token-overlap strategies.
3. Per-item weights and pass thresholds.
4. Duplicate-ID and maximum-batch validation.
5. Persistence for comparing evaluation runs over time.

The current implementation stays local and deterministic by design.
