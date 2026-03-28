# Phase 6: Signal contract - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.  
> Decisions are captured in `06-CONTEXT.md`.

**Date:** 2026-03-27  
**Phase:** 6 — Signal contract  
**Areas discussed:** Canonical spec lock, deferred parameters, integration targets (synthesis — no interactive menu)

---

## Session mode

| Aspect | Outcome |
|--------|---------|
| **Interactive gray-area pick** | Not used — **SIG-01** was already locked in [`.planning/SIGNAL-SPEC-ALPHA-v1.1.md`](../../SIGNAL-SPEC-ALPHA-v1.1.md) before discuss-phase; roadmap marks Phase 6 definition complete. |
| **Todo match** | 0 todos matched phase 6. |
| **Assumptions** | CONTEXT records default **α = 0.05** and a **recommended** independent bin-bootstrap protocol for **Δ_k**; planner may document alternatives if spec-compliant. |

---

## Equivalent “choices” (documented as decisions in CONTEXT)

| Topic | Options considered | Selected |
|-------|---------------------|----------|
| Canonical doc | Multiple scattered docs vs single file | **Single file:** `SIGNAL-SPEC-ALPHA-v1.1.md` |
| **α** | Unspecified vs fixed default | **0.05** for planning default (§8 still requires logging at first run) |
| **Δ_k bootstrap** | Paired vs independent bin resampling | **Recommended:** independent resampling per bin, same **B**, form **Δ** per replicate (details in PLAN.md) |

**User's choice:** N/A (synthetic session — aligns with pre-locked spec and workflow “no gray areas” path).

**Notes:** If the user revises **α** or bootstrap protocol before `/gsd-plan-phase 6`, edit `06-CONTEXT.md` **D-04** / **D-05** and amend `SIGNAL-SPEC-ALPHA-v1.1.md` §8 only through a formal spec revision (avoid silent drift).

---

## Claude's Discretion

- Implementation-level bootstrap edge cases (small **n_k**, seeds) — see CONTEXT § Claude's Discretion.

## Deferred Ideas

- None captured in this session.
