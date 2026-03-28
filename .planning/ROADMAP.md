# Roadmap: ContextCliff

## Milestones

- **v1.0 — Architecture reset (Omega)** — Shipped **2026-03-28**. Full phase detail: [.planning/milestones/v1.0-ROADMAP.md](milestones/v1.0-ROADMAP.md).
- **v1.1 — Signal validation (Alpha)** — **Active.** Phases **6–12** below (continues numbering after v1.0 Phase 5).

## Active roadmap (v1.1)

**Execution order:** 6 → 7 → 8 → 9 → 10 → 11 → 12 (sequential unless a later plan notes parallel work).

### Overview

| Phase | Name | Requirements | Goal (one line) |
|-------|------|--------------|-----------------|
| 6 | Signal contract | SIG-01 | Lock definitions, formulas, thresholds before behavior changes. |
| 7 | Controlled dataset | SIG-02 | Minimal synthetic data with expected degradation by length/burial. |
| 8 | Baseline API validation | SIG-03 | One model, multiple bins, scores / variance / failures. |
| 9 | Statistical robustness | SIG-04 | Bootstrap CIs, bin comparisons, resample stability. |
| 10 | Transition validation | SIG-05 | One cliff rule; stability across runs on controlled data. |
| 11 | External consistency sanity | SIG-06 | Directional check vs imported external KV only. |
| 12 | Alpha report & contract | SIG-07, SIG-08 | Interpretable report; Omega boundaries preserved. |

---

## Phase details

### Phase 6: Signal contract

**Goal:** Satisfy **SIG-01** — canonical signal spec (variance, degradation, cliff; formulas, thresholds, real-effect criteria).

**Canonical artifact (locked):** [.planning/SIGNAL-SPEC-ALPHA-v1.1.md](SIGNAL-SPEC-ALPHA-v1.1.md) — **2026-03-27.** Decisions **L1–L3** are immutable for Alpha (degradation, Δ(score) cliff, bootstrap **B**).

**Depends on:** Nothing (first phase of v1.1).

**Requirements:** SIG-01

**Success criteria:**

1. A reader can answer what counts as variance, degradation, and a cliff in this milestone without ambiguity.
2. Thresholds and “real effect” rules are stated clearly enough to implement and test.
3. Spec is frozen (versioned or dated) before primary controlled runs in later phases.

**Plans:** Definition deliverable **complete**; optional `/gsd-plan-phase 6` only for tracing implementation work against the locked spec.

**UI hint:** no

---

### Phase 7: Controlled dataset

**Goal:** Satisfy **SIG-02** — one minimal synthetic dataset with monotonic context length and systematic answer burial / noise; known answers.

**Depends on:** Phase 6 (definitions inform labeling and metrics).

**Requirements:** SIG-02

**Success criteria:**

1. Dataset is reproducibly buildable from repo artifacts (generator + fixtures or documented procedure).
2. Expected degradation direction is documented (what should worsen as length/burial increases).
3. Data loads through the existing prepare path without new CLI commands.

**Plans:** [`07-01-PLAN.md`](phases/07-controlled-dataset/07-01-PLAN.md) (`/gsd-execute-phase 7`)

**UI hint:** no

---

### Phase 8: Baseline API validation

**Goal:** Satisfy **SIG-03** — API (or mock) baseline across length bins; per-bin scores, variance/spread, failure rates.

**Depends on:** Phase 7

**Requirements:** SIG-03

**Success criteria:**

1. One defined model/configuration runs over all bins with results in SQLite.
2. Per-bin aggregates for score, variance (or IQR/std as per SIG-01), and failure rate are extractable.
3. No in-repo KV execution; mock allowed for dry checks.

**Plans:** TBD (`/gsd-plan-phase 8`)

**UI hint:** no

---

### Phase 9: Statistical robustness

**Goal:** Satisfy **SIG-04** — bootstrap CIs, bin-to-bin comparisons, resample/repeat stability; parameters documented.

**Depends on:** Phase 8

**Requirements:** SIG-04

**Success criteria:**

1. Bootstrap (or equivalent) intervals documented with iteration count and seed policy.
2. Bin-to-bin comparisons are defined and computed (not ad hoc post-selection).
3. Repeated runs or resamples show reported stability metrics.

**Plans:** TBD (`/gsd-plan-phase 9`)

**UI hint:** no

---

### Phase 10: Transition validation

**Goal:** Satisfy **SIG-05** — one canonical cliff rule evaluated on controlled data; cliffs stable across runs.

**Depends on:** Phase 9

**Requirements:** SIG-05

**Success criteria:**

1. Exactly one primary cliff rule is designated for Alpha and implemented consistently with SIG-01.
2. Detected transitions are compared across repeated runs (or bootstrap) and summarized.
3. False positives (random spikes) are distinguishable from reproducible cliffs per spec.

**Plans:** TBD (`/gsd-plan-phase 10`)

**UI hint:** no

---

### Phase 11: External consistency sanity

**Goal:** Satisfy **SIG-06** — cross-check analysis outputs against **imported** external KV-style results only; not primary ground truth.

**Depends on:** Phase 10 (internal pipeline outputs exist).

**Requirements:** SIG-06

**Success criteria:**

1. Imported runs remain explicitly labeled; report states limitations.
2. Comparison is directional/consistency only (no equivalence claim without evidence).
3. No new runtime integration for KV factories.

**Plans:** TBD (`/gsd-plan-phase 11`)

**UI hint:** no

---

### Phase 12: Alpha report & contract closure

**Goal:** Satisfy **SIG-07**, **SIG-08** — single interpretable Alpha report; Omega contract boundaries restated and honored.

**Depends on:** Phase 11 (or Phase 10 if SIG-06 skipped by plan—default is to include SIG-06).

**Requirements:** SIG-07, SIG-08

**Success criteria:**

1. Report answers “where signal appears” or “harness fails to detect signal” in plain language.
2. Score trend, variance, failures, and cliffs are readable by a human reviewer.
3. No new CLI; no implied parity of imported vs internal without labels; no in-repo KV as supported execution.

**Plans:** TBD (`/gsd-plan-phase 12`)

**UI hint:** no

---

## Inherited v1.0 gaps (optional)

**DOC-01, DOC-02, RUN-01** — add a phase or sub-plan only if `/gsd-plan-phase` shows they block SIG interpretation. Otherwise keep in backlog.

---

## Progress (v1.1)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 6. Signal contract | 0/? | **Complete** (PR #5 merged) | 2026-03-28 |
| 7. Controlled dataset | 0/? | Not started | — |
| 8. Baseline API validation | 0/? | Not started | — |
| 9. Statistical robustness | 0/? | Not started | — |
| 10. Transition validation | 0/? | Not started | — |
| 11. External consistency sanity | 0/? | Not started | — |
| 12. Alpha report & contract | 0/? | Not started | — |

---

*Roadmap created: 2026-03-27 — v1.1 Signal validation (Alpha), phases 6–12*
