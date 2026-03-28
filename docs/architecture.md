# ContextCliff architecture

## Current execution model

- **In-repo inference** uses a **remote API** (OpenAI-compatible `OpenAIClient`) or the **`mock`** backend for dry runs. There is **No in-repository KV** compression runtime, no local inference servers, and **no** CLI flags for compression budgets or third-party cache policies.
- Experiments that require custom KV-cache behavior run **outside** this repository; results can be merged into the same SQLite reporting pipeline with **`contextcliff import`** (versioned JSON artifact, required **`--run-id`** and **`--label`**, optional **`--artifact-ref`**; **`--replace`** only overwrites prior **imported** rows—never internal harness runs).
- The CLI commands are **`prepare`** → **`run`** → **`import`** → **`profile`** (see package entry `contextcliff` in `pyproject.toml`).

## Persistence

SQLite **`state.db`** stores **`runs`** (one row per logical run: provenance via **`run_source`** **`internal`** | **`imported`**, optional **`external_label`** / **`artifact_ref`**) and **`predictions`** (per-example scores and outputs keyed by **`run_id`**). Internal API/mock executions register a **`runs`** row at **`Runner.run()`** start; **`contextcliff import`** inserts **`imported`** rows from a JSON file (`schema_version`, `run_metadata`, `predictions` array).

## Documentation map

| Document | Role |
|----------|------|
| [README.md](../README.md) | One-paragraph identity and execution contract; links here for detail. |
| **This file** | Source of truth for structure and how runs work today. |
| [archive/](archive/README.md) | Historical or superseded long-form writeups only—not a contract for shipped behavior. |

## Repository layout (actual)

```
src/contextcliff/
  cli/main.py          # Click CLI: prepare, run, import, profile
  import_bridge/       # JSON artifact v1 parser (IMP-01)
  data/                # Formats, sampler, HF adapters
  models/              # ModelClient, OpenAIClient
  runner/              # Runner, StateManager (SQLite)
  eval/                # Metrics (F1, EM)
  analysis/            # Binning, cliff report
```

Legacy diagrams in `docs/archive/` may show extra folders; trust the tree above for the codebase.

## Related

- Package metadata: `pyproject.toml`
- Project description: natural-length distribution analysis for long-context QA degradation (“the cliff”).
