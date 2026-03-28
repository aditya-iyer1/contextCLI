---
phase: 07-controlled-dataset
plan: "01"
subsystem: testing
tags: [tiktoken, extractive-qa, manifest, SIG-02]
requires:
  - phase: 6
    provides: SIGNAL-SPEC-ALPHA definitions for EM / degradation language
provides:
  - Seedable `alpha_synthetic` generator and `prepare --dataset alpha_synthetic` path
  - Documentation in DATASET-SIG02 Implementation summary
affects: [Phase 8 baseline runs]
tech-stack:
  added: []
  patterns: [Designed bins via generator metadata; quantile path unchanged for narrativeqa]
key-files:
  created:
    - src/contextcliff/data/alpha_synthetic_generator.py
    - src/contextcliff/data/adapters/alpha_synthetic.py
    - tests/test_alpha_synthetic.py
  modified:
    - src/contextcliff/data/sampler.py
    - src/contextcliff/cli/main.py
    - .planning/DATASET-SIG02.md
key-decisions:
  - "Prefix filler scales with alpha_bin; needle line holds <<<answer>>> for extractive QA."
  - "prepare uses N_PER_BIN_DEFAULT (10) for alpha_synthetic; --bins is K strata."
requirements-completed: [SIG-02]
duration: —
completed: 2026-03-28
---

# Phase 7: Controlled dataset — Plan 07-01 Summary

**Delivered a deterministic `alpha_synthetic` corpus with designed bins, monotonic token length by bin, and `contextcliff prepare` wiring—no new CLI commands.**

## Performance

- **Tasks:** 4
- **Files:** generator, adapter, sampler + CLI, tests, DATASET-SIG02

## Accomplishments

- Generator `build_alpha_synthetic_examples` with `ALPHA_SIG02_SEED`, `SYNTHETIC_VERSION`, tiktoken `o200k_base` / `cl100k_base` fallback.
- `balance_samples` dispatches synthetic path vs unchanged narrativeqa quantile path.
- Pytest coverage for determinism, monotonic min tokens per bin, and CLI manifest smoke.

## Self-Check: PASSED

- Key files exist; `uv run pytest tests/test_alpha_synthetic.py -q` passes.
