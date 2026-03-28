---
phase: 02-run-provenance-in-sqlite
plan: 02-01
subsystem: database
tags: [sqlite, provenance, runs]

requires:
  - phase: "01"
    provides: "Clean docs and CLI contract"
provides:
  - "runs.run_source, external_label, artifact_ref with idempotent migration"
  - "register_internal_run + Runner.run() registration"
affects: ["analysis (optional JOIN runs later)", "Phase 3 import"]

tech-stack:
  added: []
  patterns: ["Migration after predictions table exists; backfill orphan run_ids"]

key-files:
  created: []
  modified:
    - "src/contextcliff/runner/state.py"
    - "src/contextcliff/runner/engine.py"
    - "docs/architecture.md"

key-decisions:
  - "Backfill INSERT runs after predictions table exists (fixes empty-DB init order)"
  - "ON CONFLICT for register_internal_run clears external_label/artifact_ref for internal re-runs"

patterns-established:
  - "StateManager._migrate_runs_provenance runs once per _init_db after schema stable"

requirements-completed: [STA-01]

duration: —
completed: 2026-03-28
---

# Phase 2: Run provenance — Plan 02-01 Summary

**SQLite `runs` rows now carry internal/import-ready provenance columns; the harness registers internal runs at `Runner.run()` start.**

## Performance

- **Tasks:** 5 (schema/migration, API, engine hook, smoke, docs)
- **Files modified:** 3

## Accomplishments

- Idempotent `ALTER` for `run_source`, `external_label`, `artifact_ref`; `UPDATE` safety + backfill from `predictions`.
- `register_internal_run` with JSON `config` and conflict policy documented for internal-only use.
- `Runner.run()` calls registration before cost check and example loop.

## PRAGMA table_info(runs) (fresh temp DB)

```
(0, 'run_id', 'TEXT', 0, None, 1)
(1, 'timestamp', 'DATETIME', 0, 'CURRENT_TIMESTAMP', 0)
(2, 'config', 'TEXT', 0, None, 0)
(3, 'run_source', 'TEXT', 1, "'internal'", 0)
(4, 'external_label', 'TEXT', 0, None, 0)
(5, 'artifact_ref', 'TEXT', 0, None, 0)
```

## Smoke query (`uv run` — mock Runner, 2 examples)

```sql
SELECT run_id, run_source, external_label, artifact_ref FROM runs WHERE run_id = 'smoke-run-1';
```

Result: `('smoke-run-1', 'internal', None, None)`

## Self-Check: PASSED

- `rg "failure_type" src/contextcliff/runner/state.py` → no matches
- `rg "imported" src/contextcliff/runner/engine.py` → no matches
- `rg "\.planning/" docs/architecture.md` → no matches
