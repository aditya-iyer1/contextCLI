# Phase 2: Run provenance in SQLite — Context

**Gathered:** 2026-03-28  
**Status:** Ready for planning

<domain>
## Phase Boundary

Extend **`state.db`** so **run-level provenance** satisfies **STA-01**: every run can be classified as **`internal`** (API/mock execution via this harness) vs **`imported`** (merged from external experiments in Phase 3). Deliver **schema changes**, **backward-compatible migration**, and **internal run registration** (`Runner` inserts into `runs` at start). **Do not** implement import parsing, CLI import commands, or writing `imported` rows—that is **Phase 3 (IMP-01)**. **Do not** add `failure_type` columns to `predictions` in this phase.

</domain>

<decisions>
## Implementation Decisions

### Provenance storage (runs-level columns)

- **D-01:** Add columns on **`runs`** (not on `predictions` for provenance duplication):
  - `run_source` — text constrained to **`internal`** | **`imported`** (store as `TEXT` + app-level validation; SQLite has no native enum).
  - `external_label` — `TEXT NULL` — freeform label when source is imported (Phase 3); nullable for internal.
  - `artifact_ref` — `TEXT NULL` — pointer to external artifact (path/URI/blob id); nullable for internal.
- **D-02:** **`predictions`** keep only existing columns + existing keys; provenance is resolved by **`run_id` → `runs`** join. No `run_source` columns on `predictions`.
- **D-03:** **`Runner`** must **`INSERT` (or upsert) a `runs` row** at run start for **internal** runs with `run_source='internal'`, `external_label=NULL`, `artifact_ref=NULL` (or omit nullable fields per insert style).

### Legacy databases

- **D-04:** Migration sets **`run_source = 'internal'`** for any **existing** `runs` rows (or backfills `runs` if empty—see implementation note: predictions may exist without runs today; migration may need to **insert** minimal `runs` rows from distinct `run_id` in `predictions` with `internal` defaults).
- **D-05:** No **`unknown`** state and **no** interactive prompts during migration.

### Phase boundary (strict split)

- **D-06:** **Phase 2 only:** schema + migration + internal registration path.  
- **D-07:** **Phase 3 only:** import CLI, parsing external artifacts, inserting runs with `run_source='imported'` and populating `external_label` / `artifact_ref` as required. **No** import write path stub in Phase 2 beyond schema readiness.

### failure_type

- **D-08:** **Defer** persisting `EvalRecord.failure_type` to `predictions` — **out of scope for Phase 2**; keeps Phase 2 aligned strictly to **STA-01** provenance.

### User-facing docs

- **D-09:** If `docs/` or `README` mention DB shape, follow Phase 1 rule: **no `.planning/` links**; describe behavior in **`docs/architecture.md`** only when user-facing updates are needed.

### Claude's Discretion

- Exact migration implementation (`PRAGMA user_version`, one-shot ALTER, or idempotent `_migrate_*` helpers).
- Whether to use `INSERT OR REPLACE` vs `INSERT OR IGNORE` for `runs` registration.
- JSON shape for optional future `runs.config` if retained alongside new columns.

</decisions>

<canonical_refs>
## Canonical References

**Implementers must read:**

### Scope and requirements

- `.planning/REQUIREMENTS.md` — **STA-01**
- `.planning/PROJECT.md` — persistence / import boundaries

### Current persistence

- `src/contextcliff/runner/state.py` — `StateManager`, `runs` / `predictions` tables
- `src/contextcliff/runner/engine.py` — where to hook run start / `StateManager`

### User-facing architecture (if docs updated)

- `docs/architecture.md` — execution model; add a short **Persistence** bullet only if needed for honesty (no `.planning/` links)

</canonical_refs>

<code_context>
## Existing Code Insights

### Current state

- `runs` table exists but is **not** populated by `Runner` today.
- `predictions` holds per-example rows; **`get_run_data`** drives analysis.

### Integration points

- **`Runner.__init__` or `run()`** — natural place to register an internal run after `StateManager` init.
- **`StateManager`** — centralize migration + `save_run` / `ensure_run` helpers.

</code_context>

<specifics>
## Specific Ideas

- Runs-level columns: `run_source`, `external_label`, `artifact_ref`.
- Legacy: default **`internal`** everywhere; backfill **`runs`** from distinct `predictions.run_id` if needed.
- Strict: Phase 3 owns import writes; Phase 2 does not touch `failure_type` on predictions.

</specifics>

<deferred>
## Deferred Ideas

- **IMP-01** — Import bridge and `imported` run inserts — Phase 3.
- **`failure_type` column** on predictions — future phase / separate REQ.
- **Populate `runs.config`** — only if still useful after new columns; optional.

</deferred>

---

*Phase: 02-run-provenance-in-sqlite*  
*Context gathered: 2026-03-28*
