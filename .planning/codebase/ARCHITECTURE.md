# Architecture

## Purpose

**ContextCliff** is a CLI for profiling how LLM QA performance degrades with context length (“Natural Length Distribution Analysis” / cliff detection). Flow: **prepare** (sample & manifest) → **run** (inference + metrics) → **profile** (bin, detect cliff, report).

## Layering

1. **CLI** (`src/contextcliff/cli/main.py`): `click` group with `prepare`, `run`, `profile`
2. **Data pipeline**: Adapters (`data/adapters/*`) stream `Example` objects; `data/sampler.py` implements quantile binning and writes `manifest.json`
3. **Execution** (`runner/engine.py`): `Runner` loads manifest JSON into `Example`, calls `ModelClient`, evaluates with `eval/metrics.py`, persists via `StateManager`
4. **Models** (`models/`): `ModelClient` ABC; `OpenAIClient` + inline `MockClient` in `engine.py` for dry runs
5. **Analysis** (`analysis/`): `ResultBinner` reads SQLite into pandas; `CliffProfiler` applies heuristics and markdown reporting

## Data flow

```
HF NarrativeQA (stream) → NarrativeQAAdapter → Example
                              ↓
                    sampler.balance_samples → manifest.json (list of serialized Examples)
                              ↓
                    Runner reads manifest → prompt string per example → ModelClient.generate
                              ↓
                    evaluate_example → EvalRecord → StateManager.save_prediction → state.db
                              ↓
                    profile: ResultBinner.load_run_data → bin_results → CliffProfiler → report_*.md
```

## Key abstractions

- **`Example`** / **`Prediction`** / **`EvalRecord`**: Dataclasses in `src/contextcliff/data/formats.py`; single source of truth for manifest shape and DB-backed metrics
- **`BaseAdapter`**: `load_stream() -> Iterator[Example]` (`src/contextcliff/data/adapters/base.py`)
- **`ModelClient`**: `generate`, `get_token_usage`, `cost_estimate` (`src/contextcliff/models/client.py`)

## Entry points

- **Console:** `contextcliff` → `contextcliff.cli.main:main` (`pyproject.toml`)
- **Direct:** `python -m contextcliff.cli.main` if package layout allows (standard pattern)

## Error handling in runs

- Transient API errors: retries in `OpenAIClient.generate`
- Per-example failure: caught in `Runner.run`, recorded as prediction with error-derived `failure_type` in `EvalRecord` (`ContextLengthExceeded`, `RateLimitError`, etc.)

## Cliff detection (high level)

- `CliffProfiler.detect_cliff()` (`src/contextcliff/analysis/cliff.py`) compares each length bin’s mean F1 and variance to a baseline from the first bins; sets `safe_cap_tokens` when thresholds fail
