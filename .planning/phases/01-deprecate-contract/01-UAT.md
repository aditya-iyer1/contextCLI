---
status: complete
phase: 01-deprecate-contract
source:
  - 01-01-SUMMARY.md
started: "2026-03-28T00:00:00Z"
updated: "2026-03-28T12:15:00Z"
---

## Current Test

[testing complete]

## Tests

### 1. README execution contract
expected: README shows API/mock-only contract and link to docs/architecture.md only; no .planning references.
result: pass

### 2. CLI help epilog
expected: Running `PYTHONPATH=src python -m contextcliff.cli.main --help` prints group help and an epilog that mentions mock and docs/architecture.md, and states no KV-cache/compression controls.
result: pass

### 3. Architecture source of truth
expected: Opening docs/architecture.md: file has heading "Current execution model", states API and mock, states "No in-repository KV", and mentions an import path for external results in a later milestone. No .planning/ links in this file.
result: pass

### 4. Specifications stub
expected: Opening docs/specifications.md: short stub pointing to archive/specifications.md and docs/architecture.md; no .planning links.
result: pass

## Summary

total: 4
passed: 4
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

(none)
