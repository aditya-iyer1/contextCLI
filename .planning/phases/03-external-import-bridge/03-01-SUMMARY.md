---
phase: 03-external-import-bridge
plan: 03-01
subsystem: cli
tags: [import, sqlite, IMP-01]

requires:
  - phase: "02"
    provides: "runs provenance columns"
provides:
  - "contextcliff import + JSON v1 parser"
  - "StateManager.import_external_run collision rules"
  - "Report provenance line"
affects: ["profile", "architecture docs"]

tech-stack:
  added: []
  patterns: ["Parameterized SQL in binning load_run_data"]

key-files:
  created:
    - "src/contextcliff/import_bridge/artifact_v1.py"
    - "tests/fixtures/import_v1_min.json"
    - "tests/test_import_bridge.py"
  modified:
    - "src/contextcliff/runner/state.py"
    - "src/contextcliff/cli/main.py"
    - "src/contextcliff/analysis/cliff.py"
    - "src/contextcliff/analysis/binning.py"
    - "docs/architecture.md"

key-decisions:
  - "schema_version 1 only; parse_artifact_v1 validates"
  - "internal run_id blocks import; replace only for imported"

requirements-completed: [IMP-01]

duration: —
completed: 2026-03-28
---

# Phase 3: External import bridge — Plan 03-01 Summary

**`contextcliff import` ingests versioned JSON into `state.db` as `run_source=imported`; `profile` reports a one-line provenance header.**

## Smoke (`uv run`)

```text
Imported run 'imp_test' into /tmp/timport.db
...
# ContextCliff Report: Run imp_test

**Provenance:** run_source=`imported` · external_label=`ext-lab`
```

## Tests

`python -m unittest tests.test_import_bridge -v` — 3 passed.

## Self-Check: PASSED

- `rg "schema_version" src/contextcliff/import_bridge/` — present
- Import help lists `--run-id`, `--label`, `--replace`
