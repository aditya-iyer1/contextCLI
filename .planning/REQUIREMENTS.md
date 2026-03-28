# Requirements: ContextCliff (architecture reset)

**Defined:** 2026-03-27  
**Core Value:** Trustworthy, comparable long-context evals—API execution in-repo; external compression experiments enter via import and are explicitly labeled.

Scope is the **Omega reset** (architecture reset milestone) only—no feature expansion beyond harness clarity, provenance, import, and analysis integration.

## v1 Requirements

### Documentation & contract

- [ ] **DOC-01**: Listed design docs (`docs/full_desc.md`, `docs/blueprint.md`, `docs/architecture_preview.md`, `docs/data_layer.md`) do not present in-repo SnapKV, PyramidKV, KVCache-Factory, vLLM `--kv_policy`, or similar **as shipped behavior**; aspirational or historical content is removed or clearly marked **deprecated** with a pointer to the current model (API/mock in-repo; compression via external runs + import).
- [ ] **DOC-02**: One canonical location (`README.md` or `docs/architecture.md`) states: **in-repo execution is API or `mock` only**; KV-compression and local engine studies are **out-of-repo** and may be merged via the **import** path.
- [ ] **DOC-03**: After code changes stabilize, `.planning/codebase/*.md` is updated so STACK/ARCHITECTURE/INTEGRATIONS match the reset (no stale KV-runtime narrative).

### Runner & CLI surface

- [ ] **RUN-01**: `contextcliff` CLI and `Runner` code path expose **no** flags, options, or branches that imply in-repository KV compression, local KVCache-Factory execution, or request-time `kv_budget` (or equivalent) on API backends.

### Persistence

- [x] **STA-01**: `state.db` schema (or compatible extension) records **run provenance** that distinguishes **internal** API/mock runs from **imported** runs, with a **backward-compatible** migration for existing databases.

### Import

- [x] **IMP-01**: User can **import** an external artifact (format defined in implementation) via CLI; stored predictions/runs are **persisted in SQLite** and **retrievably labeled** as imported/external.

### Analysis & reporting

- [ ] **ANA-01**: Cliff/report pipeline supports **documented** optional filtering for **compression-active** cases and **short-document suppression** when applicable inputs/metadata exist.
- [ ] **ANA-02**: Generated reports include **explicit method-fidelity caveats** when conclusions depend on run source (internal vs imported) or method assumptions.
- [ ] **ANA-03**: Reports include **positional / needle-in-haystack** diagnostics when the stored data and metadata support them.
- [ ] **ANA-04**: Report text **does not conflate** per-request **latency** with **batched throughput** where both metrics appear; wording makes the distinction clear.

### Dependencies

- [ ] **DEP-01**: If `import dotenv` (or equivalent) remains in shipped modules, **`python-dotenv` is declared** in `pyproject.toml` dependencies.

## v2 Requirements

None for this milestone. Deferred work (e.g. richer compare UI, extra datasets) is out of scope for Omega reset.

## Out of Scope

| Item | Reason |
|------|--------|
| Native KVCache-Factory / SnapKV / PyramidKV **runtime** inside this repo | Explicit PROJECT boundary |
| Multi-repo orchestration of GPU runtimes | Harness stays single-repo + import |
| Presentation polish beyond what clarity of the reset requires | Reset scope |
| Broad productization (distribution, SaaS, etc.) | Reset scope |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DOC-01 | Phase 1 | Pending |
| DOC-02 | Phase 1 | Pending |
| RUN-01 | Phase 1 | Pending |
| STA-01 | Phase 2 | Complete |
| IMP-01 | Phase 3 | Complete |
| ANA-01 | Phase 4 | Pending |
| ANA-02 | Phase 4 | Pending |
| ANA-03 | Phase 4 | Pending |
| ANA-04 | Phase 4 | Pending |
| DEP-01 | Phase 5 | Pending |
| DOC-03 | Phase 5 | Pending |

**Coverage:** v1 requirements: **11** | Mapped to phases: **11** | Unmapped: **0**

---
*Requirements defined: 2026-03-27*  
*Last updated: 2026-03-28 — IMP-01 satisfied (Phase 3 complete).*
