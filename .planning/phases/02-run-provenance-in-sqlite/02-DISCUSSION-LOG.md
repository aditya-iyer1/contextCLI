# Phase 2: Run provenance in SQLite — Discussion Log

> Audit trail. Decisions live in `02-CONTEXT.md`.

**Date:** 2026-03-28  
**Phase:** 02-run-provenance-in-sqlite  
**Mode:** defaults (user confirmed explicit decisions)

## Summary

User chose **defaults** path with locked decisions:

1. **Provenance:** `runs` columns `run_source`, `external_label`, `artifact_ref`; `Runner` inserts `runs` row at internal run start; predictions only via `run_id`.
2. **Legacy:** All existing data treated as `internal`; no unknown/prompts.
3. **Boundary:** Phase 2 = schema + migration + internal registration; Phase 3 = import + `imported` writes.
4. **`failure_type`:** Deferred; no `predictions` schema change in Phase 2.

## User verbatim (structured)

- `run_source`: `"internal"` | `"imported"`
- Nullable: `external_label`, `artifact_ref`
- No provenance duplication on `predictions`
- No partial import in Phase 2
- No `failure_type` / predictions schema in Phase 2
