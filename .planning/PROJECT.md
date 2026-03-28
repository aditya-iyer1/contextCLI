# ContextCliff

## What This Is

**ContextCliff** is a Python CLI and SQLite-backed harness for **long-context degradation analysis**: sample or fix eval cases by natural length, run models via **API-style execution only**, score predictions, bin results by length, and report “cliff” behavior (where QA quality or stability falls off). The **v1.0** milestone delivered a **brownfield architecture reset**: a reusable evaluation harness, **SQLite run provenance**, a **clean import path** for external experiments, **analysis/reporting** integration, and **declared dependencies** + an accurate **codebase map**—without mixing incompatible execution semantics.

## Core Value

**Trustworthy, comparable long-context evals**: one manifest, one scoring and analysis pipeline, SQLite as the canonical store—**API execution in-repo**, **external artifacts imported and explicitly labeled**—so conclusions are not mixed across incompatible execution models.

## Current Milestone: v1.1 Signal validation (Alpha)

**Goal:** Prove the harness detects **measurable, stable, interpretable** long-context degradation and cliff signals under **controlled conditions**—not noise—using explicit signal definitions, a synthetic dataset with expected degradation, API baseline runs, statistical robustness checks, and validated transition detection.

**Primary deliverable:** One clean report that answers either **where** the system detects degradation (token/bin) or **that** it fails to detect signal (harness fails Alpha).

**Target outcomes:**

- **SIG-01** — Canonical signal spec: variance (across bins, runs, methods), degradation, transition/cliff; formulas, thresholds, real-effect criteria.
- **SIG-02** — One minimal controlled synthetic dataset with known expected degradation as context length and answer burial increase.
- **SIG-03** — One API-based baseline on that dataset across multiple length bins; per-bin scores, variance, failure rates.
- **SIG-04** — Statistical robustness: bootstrap CIs, bin-to-bin comparisons, resample stability.
- **SIG-05** — Transition detection validated on controlled data with one explicit cliff rule; stability across runs.
- **SIG-06** — Sanity cross-check of analysis outputs against **imported** external KV results only (not primary validation).
- **SIG-07** — One interpretable report: score, variance, failure clustering, cliff behavior.
- **SIG-08** — Omega contract preserved: no in-repo KV runtime, no new CLI surface, no equivalence of imported vs internal runs without labels.

**User workflow:** Use the existing **prepare → run → import → profile** pipeline where possible (Omega mental model).

**Hard constraints:** No new architecture; no new CLI commands; no KV runtime reintegration; refactors only if required for signal-measurement validity; every change must improve signal detection validity; **API or mock execution only** in-repo; external KV results for sanity cross-check only, not primary validation.

**Alpha passes only if:** measurable degradation across length bins; stability under bootstrap / repeated runs; transition detection finds reproducible cliffs, not random spikes; outputs let a human say where performance breaks and where variance rises. **If the controlled dataset does not show expected signal, the harness fails Alpha.**

**SIG-01 (Phase 6 — locked):** Canonical signal spec — [.planning/SIGNAL-SPEC-ALPHA-v1.1.md](SIGNAL-SPEC-ALPHA-v1.1.md). Immutable decisions: **L1** degradation = soft monotonic + CI separation; **L2** cliff = **Δ(score)** between adjacent bins; **L3** all CIs = **bootstrap** with one global **B** (fixed at first use). No dataset or code changes in Phase 6.

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

### Active (v1.1 Alpha)

Signal validation (see `.planning/REQUIREMENTS.md`):

- [x] **SIG-01** — Canonical signal spec locked — [SIGNAL-SPEC-ALPHA-v1.1.md](SIGNAL-SPEC-ALPHA-v1.1.md) (variance, degradation, cliff, formulas; code aligns in later phases).
- [ ] **SIG-02** — Controlled synthetic dataset with expected degradation.
- [ ] **SIG-03** — API baseline experiment across length bins.
- [ ] **SIG-04** — Statistical robustness (bootstrap, bin comparisons, resample stability).
- [ ] **SIG-05** — Transition/cliff rule validation on controlled data.
- [ ] **SIG-06** — Imported external KV cross-check (sanity only).
- [ ] **SIG-07** — Interpretable Alpha report.
- [ ] **SIG-08** — Omega contract boundaries preserved.

**Inherited from v1.0 (schedule in Alpha only if they block valid signal interpretation or mislead on runtime semantics):**

- [ ] **DOC-01** — Long-form design docs: no misleading in-repo KV as shipped; deprecate or redirect where needed.
- [ ] **DOC-02** — Single canonical statement: API/mock in-repo; compression via import.
- [ ] **RUN-01** — CLI + `Runner` audit: no `kv_budget`-style or local KV engine hooks.

### Out of Scope

- Full native **KVCache-Factory** (or similar) inside this repo.
- **Multi-repo GPU orchestration** — harness stays single-repo + import.
- **New architecture**, **new CLI commands**, **broad UX** — same as Omega; Alpha is validation, not feature expansion.
- **Presentation polish** beyond clarity of the harness and the Alpha report.
- **Broad productization** (distribution, SaaS, etc.).

## Context

- **Brownfield:** Codebase map under `.planning/codebase/`; DOC-01/02 may still need alignment.
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
| Alpha = signal validity under control, not architecture change | Prove harness before expanding surface | v1.1 |

## Evolution

This document evolves at milestone boundaries.

**After v1.0:** Use `/gsd-new-milestone` for requirements and roadmap; keep **DOC-01 / DOC-02 / RUN-01** visible until closed or explicitly deferred.

---
*Last updated: 2026-03-27 — SIG-01 signal spec locked (Phase 6 definition)*
