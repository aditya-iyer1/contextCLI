# Phase 1: Deprecate docs & API contract — Context

**Gathered:** 2026-03-27  
**Status:** Ready for planning (updated after discuss-phase)

<domain>
## Phase Boundary

Deliver **documentation honesty** and **CLI/runner clarity** for DOC-01, DOC-02, RUN-01: remove or relocate misleading KV-era material, state the **API/mock-only** execution contract, and ensure the CLI surface matches—**before** SQLite provenance, import bridge, or analysis changes. Scope is fixed by `ROADMAP.md`; this phase does not add new runtime capabilities.

</domain>

<decisions>
## Implementation Decisions

### Deprecation shape (HARD CLEANUP)

- **D-01:** **No warnings-only** approach. Perform a **hard cleanup**: move misleading KV-era long-form docs into `docs/archive/` (or equivalent), and **remove or rewrite** any remaining content that implies in-repo KV runtime ownership, SnapKV/PyramidKV/vLLM `--kv_policy` as shipped product, or KVCache-Factory execution inside this repository.
- **D-02:** Archived files live under `docs/archive/` so the active `docs/` tree reflects current harness reality.

### DOC-02 canonical home

- **D-03:** Add a **minimal root `README.md`** containing: one-paragraph project identity; **explicit API-only contract** (in-repo execution is remote API + `mock` only); pointer to **`docs/architecture.md`** for detail.
- **D-04:** **`docs/architecture.md`** remains the **source of truth** for structure and execution model; README does not duplicate long architecture—only orients and links.

### CLI surface

- **D-05:** Update **both** module docstrings **and** user-visible CLI (`click` help, including epilog where appropriate).
- **D-06:** User-visible strings must **explicitly** state: **API/mock-only** execution in this repo; **no** KV-budget or in-process compression controls; **external** workflows for compression experiments, with results mergeable via the **import** path (detailed in later phases).

### Cross-links and audience

- **D-07:** **User-facing** docs (`README.md`, `docs/**/*.md` outside archive) **must not** reference `.planning/` or other internal planning artifacts. Cross-links stay within **`docs/`** and point readers to **`docs/architecture.md`** as the hub.
- **D-08:** This **`01-CONTEXT.md`** file may still cite `.planning/PROJECT.md` / `REQUIREMENTS.md` for **implementer** alignment—those paths are not copied into user-facing prose.

### Plans vs context

- **D-09:** User will **`/gsd-plan-phase 1`** again after this context update so **`01-01-PLAN.md`** matches these decisions (replan intent).

### Claude's Discretion

- Exact filenames under `docs/archive/` and whether a given legacy file is moved vs. deleted after content extraction.
- Wording minutiae inside `docs/architecture.md` sections not governed above.
- Formatting of `click` epilog (within the locked bullets).

</decisions>

<canonical_refs>
## Canonical References

**Implementers should read these before editing docs or CLI.**

### User-facing hub (no `.planning/` links in shipped docs)

- `docs/architecture.md` — Source of truth for execution model and layout after Phase 1; README points here only.

### Internal scope (for alignment; do not surface in README/docs copy)

- `.planning/PROJECT.md` — Omega reset scope and non-goals.
- `.planning/REQUIREMENTS.md` — DOC-01, DOC-02, RUN-01 acceptance.
- `.planning/codebase/ARCHITECTURE.md` — Current code layering.
- `.planning/codebase/STACK.md` — Dependencies and entry points.

### Targets for hard cleanup / archive

- `docs/full_desc.md`, `docs/blueprint.md`, `docs/architecture_preview.md`, `docs/data_layer.md` — Audit; move or rewrite per D-01.

### Code touchpoints

- `src/contextcliff/cli/main.py` — Help text, epilog, group docstring.
- `src/contextcliff/runner/engine.py` — Module/class docstrings as needed for RUN-01 clarity.

</canonical_refs>

<code_context>
## Existing Code Insights

### Established patterns

- `click` command group on `main`; subcommands `prepare`, `run`, `profile`.
- `Runner` wires `OpenAIClient` or `MockClient`; no KV flags in `src/` today—decisions mainly affect **docs** and **honesty of help text**.

### Integration points

- New `README.md` at repo root; new `docs/archive/` for relocated legacy docs; expanded `docs/architecture.md` section for execution model.

</code_context>

<specifics>
## Specific Ideas

- **Hard cleanup:** archive + remove/rewrite, not banner-only deprecation.
- **README:** minimal; identity + contract + link to `docs/architecture.md`.
- **CLI:** both docstrings and `--help`; state API/mock, no KV control, import for external compression results.
- **No `.planning` in user-facing docs** — cross-links only to `docs/architecture.md`.

</specifics>

<deferred>
## Deferred Ideas

- SQLite provenance, import CLI implementation, analysis/reporting enhancements — Phases 2–4.
- Replan: run `/gsd-plan-phase 1` to refresh `01-01-PLAN.md` after this context file.

**Reviewed todos:** None folded (no todo match run this session).

</deferred>

---

*Phase: 01-deprecate-contract*  
*Context gathered: 2026-03-27 (discuss-phase update)*
