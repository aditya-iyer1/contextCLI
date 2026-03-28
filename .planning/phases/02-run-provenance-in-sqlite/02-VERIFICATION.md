---
status: passed
phase: 02-run-provenance-in-sqlite
verified: 2026-03-28
requirements: [STA-01]
---

# Phase 2 verification — Run provenance in SQLite

## Goal (ROADMAP)

STA-01 — distinguish internal vs imported runs with safe migration; core prediction rows preserved.

## Must-haves (from plans)

| Check | Evidence |
|-------|----------|
| `runs` has `run_source`, `external_label`, `artifact_ref` | `02-01-SUMMARY.md` PRAGMA output; `state.py` `_migrate_runs_provenance` |
| Backfill: no `predictions.run_id` without `runs` row | `INSERT OR IGNORE ... FROM predictions WHERE NOT EXISTS runs` |
| Internal registration at run start | `engine.py` `register_internal_run` before loop |
| No `failure_type` on `predictions` in Phase 2 | `rg failure_type state.py` — absent |
| User docs | `docs/architecture.md` **Persistence** section |

## Automated / manual checks run

- `uv run python` smoke: mock `Runner` on 2-example manifest → `runs` row `('smoke-run-1', 'internal', None, None)`.
- Fresh DB init order: migration runs after `predictions` table exists (fixes empty DB).

## Human verification

None required for this phase.

## Gaps

None.
