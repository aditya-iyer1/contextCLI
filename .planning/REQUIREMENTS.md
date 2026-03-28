# Requirements: ContextCliff — v1.1 Signal validation (Alpha)

**Defined:** 2026-03-27  
**Core Value:** Trustworthy, comparable long-context evals—prove the harness detects real, stable, interpretable degradation signal under controlled conditions (API/mock in-repo; import for external artifacts only).

**Scope:** Signal-validation milestone—not feature expansion. Primary artifact: **one interpretable Alpha report** that states where degradation is detected or that the harness fails to detect signal.

---

## v1.1 Requirements

### Signal specification (SIG)

- [x] **SIG-01**: A **canonical signal spec** exists (doc + implementable definitions) that explicitly states: variance definitions across bins, runs, and methods; **degradation** definition; **transition/cliff** definition; formulas, thresholds, and what qualifies as a **real effect** (not noise). **Locked:** [.planning/SIGNAL-SPEC-ALPHA-v1.1.md](SIGNAL-SPEC-ALPHA-v1.1.md) (2026-03-27).

### Data & execution

- [ ] **SIG-02**: **One minimal controlled synthetic dataset** is added with **known expected degradation** as context length increases and answer burial / distractor noise increases systematically; ground-truth answers are always defined.

- [ ] **SIG-03**: **One API-based baseline experiment** runs on that dataset across **multiple length bins**, recording per-bin **scores**, per-bin **variance** (or spread), and **failure rates**; execution is API or mock only—no in-repo KV runtime.

### Statistics & detection

- [ ] **SIG-04**: **Statistical robustness checks** are implemented for Alpha analysis: bootstrap confidence intervals (or equivalent), bin-to-bin comparisons, and resample / repeat-run stability checks—documented with parameters (e.g., iterations, seed policy).

- [ ] **SIG-05**: **Transition detection** is validated on the controlled dataset using **one clearly defined cliff rule** (e.g., delta score, threshold crossing, failure jump, variance explosion—**one canonical choice** for Alpha); stability of detected cliffs across repeated runs is reported.

### Cross-check & reporting

- [ ] **SIG-06**: The same classes of analysis outputs are **cross-checked** against **imported external KV (or KVCache-Factory) results** only as a **sanity / directional consistency** check—not primary validation; provenance and labeling stay honest.

- [ ] **SIG-07**: **One Alpha report** presents score trends, variance, failure clustering, and detected cliff behavior in **interpretable** language so a reader can state where performance breaks and where variance rises.

- [ ] **SIG-08**: **Omega contract boundaries** are preserved: no in-repo KV runtime as a supported path; **no new CLI commands**; imported runs are **not** implied equivalent to internal runs without explicit labeling and caveats.

### Inherited from v1.0 (conditional)

Schedule in v1.1 **only if** required to avoid misleading interpretation of signal or runtime semantics:

- [ ] **DOC-01** — Long-form design docs: no misleading in-repo KV as shipped; deprecate or redirect where needed.
- [ ] **DOC-02** — Single canonical statement: API/mock in-repo; compression studies via import.
- [ ] **RUN-01** — CLI + `Runner` audit: no `kv_budget`-style or local KV engine hooks.

If not blocking Alpha validity, leave unchecked and track as backlog.

---

## v2 / Deferred

- Additional cliff rules beyond the one Alpha canonical rule.
- Broad UX, new engines, native KV, multi-model grids beyond baseline needs.
- Full closure of DOC-01/02/RUN-01 if deferred from v1.1.

---

## Out of Scope

| Item | Reason |
|------|--------|
| New architecture or large refactors | Milestone contract; only changes justified by signal validity |
| New CLI commands | Explicit constraint |
| In-repo KV runtime / KVCache-Factory integration | Omega contract |
| Primary validation using external KV results | SIG-06 is sanity only |
| General product polish | Alpha is harness validation |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SIG-01 | Phase 6 | Locked (definition) |
| SIG-02 | Phase 7 | Pending |
| SIG-03 | Phase 8 | Pending |
| SIG-04 | Phase 9 | Pending |
| SIG-05 | Phase 10 | Pending |
| SIG-06 | Phase 11 | Pending |
| SIG-07 | Phase 12 | Pending |
| SIG-08 | Phase 12 | Pending |
| DOC-01 | TBD if scheduled | Pending |
| DOC-02 | TBD if scheduled | Pending |
| RUN-01 | TBD if scheduled | Pending |

**Coverage:**

- v1.1 core requirements: **8** (SIG-01–SIG-08)
- Mapped to phases: **8** (conditional inherits tracked separately)
- Unmapped: **0** ✓

---
*Requirements defined: 2026-03-27*  
*Last updated: 2026-03-27 — SIG-01 locked (`SIGNAL-SPEC-ALPHA-v1.1.md`)*
