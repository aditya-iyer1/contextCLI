# Phase 5: Dependencies & codebase map — Context

**Gathered:** 2026-03-28  
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver **DEP-01** and **DOC-03** only:

1. **DEP-01** — Ensure **`pyproject.toml`** declares every dependency implied by **shipped** `src/` imports (at minimum resolve **`python-dotenv`**, which is imported for `load_dotenv` in **`openai_client.py`** and **`narrative_qa.py`** but was historically missing from declared deps — see existing note in `.planning/codebase/STACK.md`).

2. **DOC-03** — Refresh **`.planning/codebase/*.md`** so **STACK**, **ARCHITECTURE**, **INTEGRATIONS**, **STRUCTURE**, and related map files reflect the **post–Phase 4** codebase: **`import_bridge`**, extended **`profile`** / **`profile_report`** / **`ReportExtras`**, provenance-aware reporting, API-only execution story—**without** reintroducing a KV-runtime-as-shipped narrative.

**Out of scope for this phase:** Phase 1 requirements **DOC-01**, **DOC-02**, **RUN-01** (listed design docs and runner-flag audit remain separate unless the roadmap is explicitly changed). Do not expand Phase 5 into a full documentation rewrite of `docs/full_desc.md` etc.

</domain>

<decisions>
## Implementation Decisions

### DEP-01 (dependencies)

- **D-01:** Add **`python-dotenv`** to **`[project].dependencies`** in **`pyproject.toml`** with a **compatible version constraint** (e.g. lower bound or range per project convention — **Claude’s discretion**; follow how other deps are specified in the same file).
- **D-02:** Run a **shallow import audit** of **`src/contextcliff/`** (e.g. scan imports vs `pyproject.toml`) and fix any other **obvious** missing declarations discovered in shipped modules. **Do not** add optional dev-only tools to runtime deps unless they are imported at runtime.
- **D-03:** After edits, **`uv sync`** / **`uv run`** smoke (or **`python -c`** import checks) must succeed on a clean venv narrative — document the exact command in the phase plan or SUMMARY.

### DOC-03 (codebase map)

- **D-04:** Update at minimum: **`STACK.md`** (dependency table — move `python-dotenv` from “implicit” to declared; align package list with **`pyproject.toml`**), **`ARCHITECTURE.md`** (CLI commands include **`import`**; analysis path includes **`profile_report`** / optional manifest and filters; data flow diagram text updated), **`INTEGRATIONS.md`** (OpenAI + SQLite + optional HF; import path), **`STRUCTURE.md`** (tree includes **`import_bridge/`**, **`analysis/profile_report.py`**).
- **D-05:** Touch **`CONVENTIONS.md`**, **`CONCERNS.md`**, **`TESTING.md`** only where **factual drift** exists (stale paths, wrong command names). **No** wholesale rewrites.
- **D-06:** **No `.planning/` path references** in user-facing **`docs/architecture.md`** per project convention; codebase map files may reference `.planning/` internally.

### Claude's Discretion

- Exact dependency version pins vs loose constraints.
- Whether to add a one-line **`scripts/check-imports`** or rely on manual audit — only if lightweight.
- Order of file updates (single PR vs minimal commits).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap

- `.planning/REQUIREMENTS.md` — **DEP-01**, **DOC-03**
- `.planning/ROADMAP.md` — Phase 5 goal and success criteria
- `.planning/PROJECT.md` — milestone scope; what remains vs Validated

### Evidence of current drift

- `.planning/codebase/STACK.md` — notes `python-dotenv` missing from `pyproject.toml`
- `pyproject.toml` — current `[project].dependencies`
- `src/contextcliff/models/openai_client.py`, `src/contextcliff/data/adapters/narrative_qa.py` — `load_dotenv` usage

### Post-reset behavior (for accurate map text)

- `.planning/phases/03-external-import-bridge/03-CONTEXT.md` — import CLI contract
- `.planning/phases/04-analysis-reporting/04-CONTEXT.md` — analysis / profile extensions

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets

- **STACK.md** already documents the dotenv gap — DEP-01 is partly “close the documented gap.”
- **Phase 4 code:** `import_bridge/`, `analysis/profile_report.py`, `cliff.ReportExtras`, CLI `profile` options.

### Integration points

- **`pyproject.toml`** — single source for `uv` installs.
- **`.planning/codebase/*`** — consumed by GSD and humans; must match `src/` layout.

</code_context>

<specifics>
## Specific Ideas

- Keep codebase map updates **factual** (paths, commands, dependencies)—avoid aspirational architecture.

</specifics>

<deferred>
## Deferred Ideas

- Phase 1 **DOC-01 / DOC-02 / RUN-01** — separate roadmap phases / backlog; not bundled into Phase 5 unless explicitly rescoped.

### Reviewed Todos (not folded)

- None.

</deferred>

---

*Phase: 05-dependencies-codebase-map*  
*Context gathered: 2026-03-28*
