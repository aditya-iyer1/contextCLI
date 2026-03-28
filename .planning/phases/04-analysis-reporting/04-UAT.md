---
status: complete
phase: 04-analysis-reporting
source:
  - 04-01-PLAN.md (no SUMMARY.md — tests derived from plan + shipped code)
started: "2026-03-28T12:00:00.000Z"
updated: "2026-03-28T13:00:00.000Z"
---

## Current Test

[testing complete]

## Tests

### 1. Profile CLI — new options in help
expected: Help lists --manifest, --min-prompt-tokens, --max-prompt-tokens and references docs/architecture.md for optional filters/manifest.
result: pass

### 2. Report — Metrics interpretation and latency vs throughput
expected: A generated `report_<run_id>.md` includes a "### Metrics interpretation" subsection under Executive Summary with text stating `latency_ms` is per-request and that throughput must not be inferred from mean latency alone.
result: pass

### 3. Report — Caveats for imported runs
expected: For a run with `run_source=imported`, the markdown includes "## Caveats" with at least one bullet about external/imported execution and F1/EM not implying identical experimental conditions.
result: pass

### 4. Provenance line includes artifact_ref when set
expected: When the `runs` row has non-empty `artifact_ref`, the report provenance line includes `artifact_ref=`... in backticks.
result: pass

### 5. Analysis warnings — compression filter without manifest
expected: When `runs.config` JSON includes `"analysis_filters": {"compression_active_only": true}` and profile is run **without** `--manifest`, the report contains "## Analysis warnings" with text about manifest/compression filter not applied.
result: pass

### 6. Positional diagnostics — manifest with needle_position_bucket
expected: When `--manifest` points to JSON where examples include `metadata.needle_position_bucket` (string) for rows matching prediction `example_id`, the report contains "## Positional diagnostics" and a table with bucket names and mean F1.
result: pass

## Summary

total: 6
passed: 6
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none — all tests passed]
