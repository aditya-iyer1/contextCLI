---
status: complete
phase: 07-controlled-dataset
source: [07-01-SUMMARY.md]
started: "2026-03-28T12:30:00.000Z"
updated: "2026-03-28T13:15:00.000Z"
---

## Current Test

[testing complete]

## Tests

### 1. Prepare alpha_synthetic manifest
expected: From project root, `uv run contextcliff prepare --dataset alpha_synthetic --bins 4` exits 0; `manifest.json` in cwd contains examples with metadata (e.g. alpha_bin, synthetic_version) and extractive structure (answers substring of context).
result: pass

### 2. DATASET-SIG02 implementation summary
expected: `.planning/DATASET-SIG02.md` includes an "Implementation summary" subsection with `ALPHA_SIG02_SEED` (or seed 42), `sig02-v1`, and tokenizer (`o200k_base` / fallback) language.
result: pass

### 3. NarrativeQA prepare still runs
expected: `uv run contextcliff prepare --dataset narrativeqa --bins 5` does not raise a Python traceback (HF or network may limit rows; exit 0 or a clear stream message without crash is acceptable).
result: pass

### 4. Deterministic manifest for alpha_synthetic
expected: With the same `--dataset alpha_synthetic` and `--bins`, deleting `manifest.json` and running prepare again yields the same manifest content as before (byte-identical or user confirms same structure/ids).
result: pass

## Summary

total: 4
passed: 4
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none]
