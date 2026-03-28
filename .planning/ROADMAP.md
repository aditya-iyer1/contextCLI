# Roadmap: ContextCliff — Architecture reset (Omega)

## Overview

Five **coarse** phases follow the **execution order** in `PROJECT.md`: strip misleading documentation and lock the **API-only** contract first, add **SQLite provenance**, then **import**, then **analysis/reporting** lessons, then **deps + codebase map** sync. No new abstractions except what **IMP-01** requires for import.

## Phases

- [x] **Phase 1: Deprecate docs & API contract** — Remove or deprecate misleading KV-runtime narrative; canonical “API/mock only + import” story; verify CLI/runner surface (DOC-01, DOC-02, RUN-01).
- [ ] **Phase 2: Run provenance in SQLite** — Schema/migration for internal vs imported runs (STA-01).
- [ ] **Phase 3: External import bridge** — CLI + persistence path for labeled imports (IMP-01).
- [ ] **Phase 4: Analysis & reporting** — Filtering, caveats, positional diagnostics, latency vs throughput (ANA-01–ANA-04).
- [ ] **Phase 5: Dependencies & codebase map** — `python-dotenv` declaration if needed; refresh `.planning/codebase/*` (DEP-01, DOC-03).

## Phase Details

### Phase 1: Deprecate docs & API contract

**Goal:** Satisfy DOC-01, DOC-02, RUN-01 before additive work—**removal and deprecation before addition**.

**Depends on:** Nothing — first phase.

**Requirements:** DOC-01, DOC-02, RUN-01

**Success criteria:**

1. A reader can open the canonical doc and state how execution works in-repo vs import.
2. Targeted long-form docs no longer read as if vLLM/KV policies are built-in here.
3. `grep`/`rg` over `src/` and CLI help shows no KV-budget or local compression hooks.

**Plans:** 1 plan (01-01)

**UI hint:** no

Plans:

- [x] **01-01:** Audit and edit docs; add canonical architecture note; verify CLI/runner surface (see `01-01-PLAN.md`).

---

### Phase 2: Run provenance in SQLite

**Goal:** STA-01 — distinguish internal runs from imported runs with safe migration.

**Depends on:** Phase 1

**Requirements:** STA-01

**Success criteria:**

1. New or migrated DB stores provenance needed to label internal vs imported runs.
2. Existing `state.db` from prior usage still opens and migrates without data loss for core prediction rows.

**Plans:** TBD (plan in `/gsd-plan-phase 2`)

**UI hint:** no

---

### Phase 3: External import bridge

**Goal:** IMP-01 — minimal import path; no extra backends beyond parsing + SQLite write.

**Depends on:** Phase 2

**Requirements:** IMP-01

**Success criteria:**

1. A CLI entry imports a defined artifact into SQLite with mandatory external labeling.
2. Imported data can be consumed by the same reporting path as internal runs (with labels visible).

**Plans:** TBD

**UI hint:** no

---

### Phase 4: Analysis & reporting

**Goal:** ANA-01–ANA-04 — integrate KV-study lessons into reports/cliff pipeline without breaking API runs.

**Depends on:** Phase 3

**Requirements:** ANA-01, ANA-02, ANA-03, ANA-04

**Success criteria:**

1. Filters and caveats appear when enabled or when metadata demands them.
2. Positional diagnostics appear when data supports them.
3. Latency and throughput are not conflated in generated markdown.

**Plans:** TBD

**UI hint:** no

---

### Phase 5: Dependencies & codebase map

**Goal:** DEP-01, DOC-03 — declare missing deps; refresh codebase map after reset.

**Depends on:** Phase 4

**Requirements:** DEP-01, DOC-03

**Success criteria:**

1. `pyproject.toml` matches imports used in shipped code.
2. `.planning/codebase/` documents reflect post-reset architecture and integration story.

**Plans:** TBD

**UI hint:** no

---

## Progress

**Execution order:** 1 → 2 → 3 → 4 → 5 (sequential execution per `config.json`).

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Deprecate docs & API contract | 1/1 | Complete | 2026-03-28 |
| 2. Run provenance in SQLite | — | Not started | — |
| 3. External import bridge | — | Not started | — |
| 4. Analysis & reporting | — | Not started | — |
| 5. Dependencies & codebase map | — | Not started | — |

---
*Roadmap created: 2026-03-27*
