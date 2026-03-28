---
status: complete
phase: 03-external-import-bridge
source:
  - 03-01-SUMMARY.md
started: "2026-03-28T16:30:00Z"
updated: "2026-03-28T16:50:00Z"
---

## Current Test

[testing complete]

## Tests

### 1. Architecture — import documented
expected: `docs/architecture.md` mentions import + imported runs; no `.planning/` references.
result: pass

### 2. CLI — import help surface
expected: From repo root, `uv run python -m contextcliff.cli.main import --help` lists **`--run-id`**, **`--label`**, and **`--replace`**.
result: pass

### 3. End-to-end — import fixture then profile
expected: |
  From repo root (adjust DB path if needed):

  rm -f /tmp/uat3.db && uv run python -m contextcliff.cli.main import tests/fixtures/import_v1_min.json --run-id uat_imp --label "uat-label" --db /tmp/uat3.db && uv run python -m contextcliff.cli.main profile uat_imp --db /tmp/uat3.db

  Then open generated `report_uat_imp.md` in cwd: first lines after the title include **Provenance** with **imported** and **uat-label**.
result: pass

### 4. Guard — internal run_id cannot be imported over
expected: |
  `uv run python -m unittest tests.test_import_bridge.ImportBridgeTests.test_internal_blocked -v` exits 0 (pass).
result: pass

## Summary

total: 4
passed: 4
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none yet]
