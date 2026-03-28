# Architecture

## Purpose

**ContextCliff** is a CLI for profiling how LLM QA performance degrades with context length (“Natural Length Distribution Analysis” / cliff detection). End-to-end flow: **prepare** (sample & manifest) → **run** (API inference + metrics into SQLite) → optional **import** (external JSON artifacts into SQLite with provenance) → **profile** (bin, detect cliff, markdown report).

## Layering

1. **CLI** (`src/contextcliff/cli/main.py`): `click` group with `prepare`, `run`, `import`, `profile`
2. **Data pipeline**: Adapters (`data/adapters/*`) stream `Example` objects; `data/sampler.py` implements quantile binning and writes `manifest.json`
3. **Execution** (`runner/engine.py`): `Runner` loads manifest JSON into `Example`, calls `ModelClient`, evaluates with `eval/metrics.py`, persists via `StateManager` (internal runs; `run_source` = internal)
4. **Models** (`models/`): `ModelClient` ABC; `OpenAIClient` + inline `MockClient` in `engine.py` for dry runs—**API-style execution only** in-repo
5. **Import bridge** (`import_bridge/`): `artifact_v1.parse_artifact_v1` parses **`schema_version` 1** JSON; `contextcliff import` writes predictions and labels **`runs`** with **`run_source` = imported**, **`external_label`**, optional **`artifact_ref`**, via `StateManager`
6. **Analysis** (`analysis/`): `ResultBinner` reads SQLite into pandas; `profile_report` applies optional **token filters**, optional **`--manifest`** join, and builds caveat / positional / metrics-interpretation fragments; `CliffProfiler.generate_markdown_report` composes **`ReportExtras`** into the final markdown

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
        Optional: external JSON v1 artifact → contextcliff import → parse_artifact_v1 → state.db
                              (imported run rows: provenance via run_source / external_label / artifact_ref)
                              ↓
        profile: ResultBinner.load_run_data → bin_results → CliffProfiler (+ profile_report helpers;
                  optional manifest join for filters & positional diagnostics) → report_*.md
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
