# Structure

## Repository layout (high level)

```
contextCLI/
├── pyproject.toml          # Package metadata, deps, entry point
├── manifest.json           # Generated: balanced sample manifest (often gitignored in real use)
├── state.db                # Generated: SQLite run state
├── dry_run.sh              # Shell: mock run + profile smoke test
├── test.py                 # Ad hoc manifest inspection
├── verify_sampler.py       # Helper to exercise sampler (referenced by dry_run.sh)
├── debug_db.py             # DB debugging helper
├── docs/                   # Design and architecture notes (blueprint, data layer, etc.)
└── src/contextcliff/
    ├── cli/main.py         # Click CLI: prepare, run, profile
    ├── data/
    │   ├── formats.py      # Example, Prediction, EvalRecord
    │   ├── sampler.py      # balance_samples → manifest.json
    │   └── adapters/
    │       ├── base.py     # BaseAdapter
    │       └── narrative_qa.py
    ├── models/
    │   ├── client.py       # ModelClient ABC
    │   └── openai_client.py
    ├── runner/
    │   ├── engine.py       # Runner, MockClient
    │   └── state.py        # StateManager (SQLite)
    ├── eval/metrics.py     # F1, EM, evaluate_example
    └── analysis/
        ├── binning.py      # ResultBinner
        └── cliff.py      # CliffProfiler
```

## Naming conventions

- **Modules:** `snake_case` (`narrative_qa.py`, `openai_client.py`)
- **Classes:** `PascalCase` (`Runner`, `NarrativeQAAdapter`, `CliffProfiler`)
- **CLI commands:** `prepare`, `run`, `profile` on the `contextcliff` group

## Important paths (by role)

| Role | Path |
|------|------|
| Add a dataset | New module under `src/contextcliff/data/adapters/`, implement `BaseAdapter` |
| Change inference backend | `src/contextcliff/models/` + factory branch in `runner/engine.py` |
| Change metrics | `src/contextcliff/eval/metrics.py` |
| Change persistence schema | `src/contextcliff/runner/state.py` (and any readers in `analysis/binning.py`) |

## Documentation

- **`docs/`**: Human-written architecture and product notes (`architecture_preview.md`, `blueprint.md`, `data_layer.md`, etc.)—not wired into the Python package as docstrings-only docs site
