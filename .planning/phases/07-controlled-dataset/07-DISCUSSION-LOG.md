# Phase 7: Controlled dataset - Discussion Log

> **Audit trail only.** Decisions live in `07-CONTEXT.md`.

**Date:** 2026-03-28  
**Phase:** 7 — Controlled dataset  
**Areas discussed:** Dataset wiring, content model, reproducibility, metadata (synthesized — no interactive menu)

---

## Session mode

| Aspect | Outcome |
|--------|---------|
| **Gray-area selection** | Skipped — roadmap + **SIG-02** + **SIG-01** constrain choices; decisions recorded as **D-01–D-09** in CONTEXT. |
| **Todo match** | 0 matches. |

---

## Resolved topics (mapped to CONTEXT)

| Topic | Resolution |
|-------|------------|
| CLI surface | Extend **`--dataset alpha_synthetic`** only; no new subcommands. |
| Adapter | New **`AlphaSyntheticAdapter`** + `balance_samples` branch. |
| Burial / length | Monotonic bins + systematic burial; documented in **`.planning/DATASET-SIG02.md`** (to be created in execution). |
| Metric | **EM** only for Alpha primary scoring per signal spec. |
| Reproducibility | Seeded generation + optional golden JSONL for tests. |

---

## Claude's Discretion

- Exact filler templates, **K**, **n_per_bin** — see CONTEXT **Claude's Discretion**.

## Deferred ideas

- NarrativeQA as Alpha control — out of scope for SIG-02 (see CONTEXT deferred).
