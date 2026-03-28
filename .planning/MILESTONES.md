# Milestones

## v1.0 Architecture reset (Omega) (Shipped: 2026-03-28)

**Phases completed:** 5 phases, 5 plans

**Key accomplishments:**

- **Phase 1** — Canonical `docs/architecture.md`, CLI help/epilog, archive misleading specs; `rg` clean for KV-as-shipped outside `docs/archive/`.
- **Phase 2** — SQLite `runs` provenance (`run_source`, `external_label`, `artifact_ref`), migration, `register_internal_run` + `Runner` registration.
- **Phase 3** — `contextcliff import`, JSON `schema_version` 1, `import_external_run`, report provenance line.
- **Phase 4** — `profile_report`, `ReportExtras`, ANA-01–ANA-04 (filters, caveats, positional diagnostics, latency vs throughput).
- **Phase 5** — `python-dotenv` declared, `load_dotenv` scoped to CLI entry; `.planning/codebase/*` refreshed (DEP-01, DOC-03).

### Known gaps (shipped with open requirements)

The following **v1** requirements were **not** checked off in `REQUIREMENTS.md` at archive time:

| ID | Note |
|----|------|
| **DOC-01** | Long-form design docs (`docs/full_desc.md`, etc.) still need explicit deprecation / alignment pass. |
| **DOC-02** | Canonical “API/mock + import” story in README vs `docs/architecture.md` — verify single source of truth. |
| **RUN-01** | Formal audit that CLI + `Runner` expose no KV-compression or `kv_budget`-style controls. |

Track these in the **next** milestone requirements.

---
