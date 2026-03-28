# Phase 7: Controlled dataset - Discussion Log

> **Audit trail only.** Decisions live in `07-CONTEXT.md` and [`.planning/DATASET-SIG02.md`](../../DATASET-SIG02.md).

**Date:** 2026-03-28  
**Phase:** 7 — Controlled dataset  
**Areas discussed:** User-confirmed locks (2026-03-28)

---

## User selections

| # | Topic | Choice |
|---|--------|--------|
| 1 | Dataset slug | **Keep `alpha_synthetic`** |
| 2 | Bin strategy | **Equal n per bin**; bins **defined by the synthetic generator** — **not** post-hoc quantiles |
| 3 | Burial | **Needle-offset emphasis**; filler only supports realizing that knob |
| 4 | Fixtures | **Procedural first**; **no** committed golden JSONL yet — add only if determinism questionable or tests need snapshots |

## Additional locks (planning)

- Answer **always present** in context.
- **One** task only: **extractive QA**.
- **One** seedable generator.
- **Monotonic length growth** by construction.
- **Expected outcome** documented in **`.planning/DATASET-SIG02.md`** before implementation is considered done.

---

## Artifacts updated

- [`07-CONTEXT.md`](07-CONTEXT.md) — decisions **D-01–D-13**
- [`.planning/DATASET-SIG02.md`](../../DATASET-SIG02.md) — normative design contract + completion gate
