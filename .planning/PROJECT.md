# ContextCliff

## What This Is

**ContextCliff** is a Python CLI and SQLite-backed harness for **long-context degradation analysis**: sample or fix eval cases by natural length, run models via **API-style execution only**, score predictions, bin results by length, and report “cliff” behavior (where QA quality or stability falls off). The **v1.0** milestone delivered a **brownfield architecture reset**: a reusable evaluation harness, **SQLite run provenance**, a **clean import path** for external experiments, **analysis/reporting** integration, and **declared dependencies** + an accurate **codebase map**—without mixing incompatible execution semantics.

## Core Value

**Trustworthy, comparable long-context evals**: one manifest, one scoring and analysis pipeline, SQLite as the canonical store—**API execution in-repo**, **external artifacts imported and explicitly labeled**—so conclusions are not mixed across incompatible execution models.

## Current state (v1.0)

**Shipped:** 2026-03-28 — **Architecture reset (Omega)**. See [.planning/MILESTONES.md](MILESTONES.md) and tag **`v1.0`**.

## Requirements

### Validated (v1.0)

- ✓ **CLI pipeline** — `prepare` → `run` → `import` → `profile`; manifest, inference, JSON import, cliff reports.
- ✓ **SQLite experiment store** — `StateManager`, resume by example ID.
- ✓ **API-path execution** — `OpenAIClient` + `ModelClient`; `mock` for dry runs.
- ✓ **Scoring** — F1, EM (`eval/metrics.py`).
- ✓ **Failure taxonomy** — `EvalRecord.failure_type` on errors in `Runner.run`.
- ✓ **Analysis & report** — `ResultBinner`, `CliffProfiler`, `profile_report` (`Phase 4`).
- ✓ **Data layer** — NarrativeQA adapter, NLDA-style sampling.
- ✓ **Run provenance (STA-01)** — internal vs imported runs, migration (`Phase 2`).
- ✓ **Import bridge (IMP-01)** — `contextcliff import`, JSON v1 (`Phase 3`).
- ✓ **Analysis & reporting (ANA-01–ANA-04)** — filters, caveats, positional diagnostics, latency wording (`Phase 4`).
- ✓ **Declared dependencies (DEP-01)** — `python-dotenv` + import audit (`Phase 5`).
- ✓ **Codebase map (DOC-03)** — `.planning/codebase/*` (`Phase 5`).

### Active (next milestone)

Documentation and contract closure not fully signed off in the v1.0 requirement checkboxes:

- [ ] **DOC-01** — Long-form design docs: no misleading in-repo KV runtime as shipped; deprecate or redirect where needed.
- [ ] **DOC-02** — Single canonical statement: API/mock in-repo; compression studies via **import**.
- [ ] **RUN-01** — CLI + `Runner` audit: no `kv_budget`-style or local KV engine hooks.

- [x] **External artifact import bridge** — v1.0 scope met; further UX later.
- [x] **Preserve analysis lessons** in reporting — v1.0 scope met (`profile_report`, `CliffProfiler`).

### Out of Scope

- Full native **KVCache-Factory** (or similar) inside this repo.
- **Multi-repo GPU orchestration** — harness stays single-repo + import.
- **Presentation polish** beyond clarity of the harness.
- **Broad productization** (distribution, SaaS, etc.).

## Context

- **Brownfield:** Codebase map under `.planning/codebase/`; older long-form docs may still need pass (DOC-01/02).
- **Constraint:** No mixed architecture where imported and API runs are presented as the same experiment type without labeling.

## Constraints

- **Execution:** API / endpoint-based paths in-repo; heavy KV work **outside**, via **import**.
- **Honesty:** No unsupported request-time `kv_budget` on API backends.
- **Storage:** SQLite canonical for in-harness and imported runs.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| API-only in-repo; KV experiments external + import | Avoid false equivalence | ✓ v1.0 |
| Imported runs explicitly labeled | Semantics preserved | ✓ v1.0 |
| `load_dotenv()` only in `cli/main.py` | Optional `.env`; no override of set env by default | ✓ v1.0 |
| prepare → run → import → profile | Preserves harness mental model | ✓ v1.0 |

## Evolution

This document evolves at milestone boundaries.

**After v1.0:** Use `/gsd-new-milestone` for requirements and roadmap; keep **DOC-01 / DOC-02 / RUN-01** visible until closed.

---
*Last updated: 2026-03-28 — after v1.0 milestone archive*
