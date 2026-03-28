# Phase 3: External import bridge — Context

**Gathered:** 2026-03-28  
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver **IMP-01**: a **CLI import path** that reads a **single versioned JSON artifact**, writes **`runs`** and **`predictions`** into **`state.db`** with **`run_source='imported'`** and **mandatory human-readable labeling**, so **profile/reporting** can consume imported runs alongside internal runs. **No** new inference backends—**parse + SQLite write** only. **No** full provenance UX in reports beyond a **minimal header** (Phase 4 may enrich).

</domain>

<decisions>
## Implementation Decisions

### Artifact format

- **D-01:** **Single file**, **versioned JSON** only—no directory bundles, no NDJSON.
- **D-02:** Top-level fields (required structure):
  - **`schema_version`** — required string (import code validates supported versions).
  - **`run_metadata`** — object (freeform but structured): model, dataset, method, budget, etc. (exact keys are implementation-defined; must be storable and/or mappable to `runs.config` JSON).
  - **`predictions`** — **array** of per-example records matching what `StateManager` / analysis expects (align columns with existing `predictions` schema; no new provenance columns on `predictions` per Phase 2).

### CLI surface

- **D-03:** New Click subcommand: **`contextcliff import`** — clearly separated from **`run`** (inference). Options/arguments defined in planning; must accept artifact path, **`--run-id`**, **`--label`**, optional **`--artifact-ref`**, DB path if not default, **`--replace`** per D-06.

### `run_id` and collision policy

- **D-04:** **`--run-id` is required** for every import.
- **D-05:** If a row in **`runs`** with that **`run_id`** already exists:
  - **Default:** **error** (exit non-zero, clear message).
  - **`--replace`:** allowed **only** when the existing row has **`run_source = 'imported'`**. Implementation updates **`runs`** metadata and **replaces** **`predictions`** for that `run_id` as specified in D-07.
  - **NEVER** overwrite or delete rows where **`run_source = 'internal'`** (hard guard; same `run_id` as internal → error, no `--replace` escape).

### Labeling (IMP-01)

- **D-06:** **`--label`** is **required**, non-empty string → maps to **`runs.external_label`**. Plain text; **no** strict length/charset validation beyond non-empty (store as SQLite TEXT).
- **D-07:** **`--artifact-ref`** optional → **`runs.artifact_ref`**; plain text (path/URI/blob id as user provides).

### Idempotency

- **D-08:** **Error by default** when **`run_id`** already exists (see D-05).
- **D-09:** **`--replace`:** overwrites **predictions** and **run-level metadata** for that **`imported`** run only (consistent with “same import slot” semantics). Exact merge rules for `runs.config` vs JSON `run_metadata` — **Claude’s discretion** in implementation plan.

### Reporting (minimal visibility)

- **D-10:** Phase 3 ensures **DB correctness** (`run_source`, `external_label` on **`runs`** for imported rows).
- **D-11:** **One-line header** (or equivalent minimal prefix) in generated markdown report including **`run_source`** and **`external_label`** when profiling a run. **No** full provenance block, tables, or Phase 4 analysis filters—deferred.

### Claude's Discretion

- Exact **`schema_version`** values supported v1 and validation error messages.
- Mapping **`run_metadata`** ↔ **`runs.config`** JSON shape.
- Per-example JSON field names → `predictions` columns (must match existing schema).
- Whether import uses **`INSERT`** helper on `StateManager` or new module—must respect D-04–D-07 guards.

</decisions>

<specifics>
## Specific Ideas

- User confirmed **defaults** path: single JSON envelope, `import` subcommand, protected `run_id`, required label, minimal report line.
- **No** NDJSON/directory formats in Phase 3.

</specifics>

<canonical_refs>
## Canonical References

**Implementers must read:**

### Scope and requirements

- `.planning/REQUIREMENTS.md` — **IMP-01**
- `.planning/PROJECT.md` — import boundary; API-only in-repo

### Prior phase (provenance contract)

- `.planning/phases/02-run-provenance-in-sqlite/02-CONTEXT.md` — `runs` vs `predictions`; `internal` vs `imported`

### Code

- `src/contextcliff/runner/state.py` — `StateManager`, `runs` / `predictions` schema
- `src/contextcliff/cli/main.py` — add `import` alongside `prepare` / `run` / `profile`
- `src/contextcliff/analysis/cliff.py` (and callers of report generation) — minimal header line for `run_source` / `external_label`

### User-facing docs (when updated)

- `docs/architecture.md` — import path summary; **no `.planning/`** links in user-facing text

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets

- **`StateManager`** — migrations, `save_prediction` pattern; import will need **`imported`** `runs` insert/update** paths that **do not** call `register_internal_run` (internal-only).
- **`ResultBinner.load_run_data`** / **`profile`** command — already key off `run_id`; imported runs join reporting once rows exist.

### Established patterns

- **Click** group in `cli/main.py` — mirror style for **`import`** (help strings, epilog consistency with Phase 1 contract).

### Integration points

- **`profile`** / **`CliffProfiler.generate_markdown_report`** — inject minimal provenance line from **`runs`** (query by `run_id`) before or in report header.

</code_context>

<deferred>
## Deferred Ideas

- **ANA-01–ANA-04** — Full caveats, filters, positional diagnostics, latency vs throughput copy — **Phase 4**.
- **Rich provenance block** in reports — **Phase 4+**.
- **NDJSON / multi-file / zip** import — backlog unless roadmap adds a phase.
- **`failure_type` on `predictions`** — still deferred unless separate REQ.

</deferred>

---

*Phase: 03-external-import-bridge*  
*Context gathered: 2026-03-28*
