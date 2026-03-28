# Phase 3: External import bridge — Discussion log

> **Audit trail only.** Not an input to planning/research/execution agents.

**Session:** 2026-03-28  

## Flow

- User invoked `/gsd-discuss-phase 3`.
- Gray areas presented: artifact format, CLI, `run_id`, labeling, idempotency, reporting.
- User chose **`defaults`** and supplied explicit decisions (numbered 1–6) in a single message.

## Record of choices

1. **Artifact:** Single versioned JSON file; `schema_version`, `run_metadata`, `predictions` list; no NDJSON/directory.
2. **CLI:** New `contextcliff import`; separate from `run`.
3. **`run_id`:** Required `--run-id`; error if exists; `--replace` only if existing `run_source = imported`; never overwrite internal.
4. **Labeling:** Required `--label` → `external_label`; optional `--artifact-ref`; plain text.
5. **Idempotency:** Error by default; `--replace` overwrites imported run predictions + metadata.
6. **Reporting:** DB correct + one-line header with `run_source` and `external_label`; full block → Phase 4.

Captured in `03-CONTEXT.md` as D-01 through D-11.
