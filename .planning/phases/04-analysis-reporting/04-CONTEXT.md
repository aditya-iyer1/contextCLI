# Phase 4: Analysis & reporting — Context

**Gathered:** 2026-03-27  
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver **ANA-01–ANA-04** by extending the existing **`profile` → `ResultBinner` → `CliffProfiler.generate_markdown_report`** pipeline and related helpers. **No** new inference backends, **no** changes to import artifact schema unless a minimal SQLite extension is required for analysis (prefer **config + optional manifest join** first).

Scope is **markdown reporting and binning behavior** that:

- Applies **optional** filters only when **documented** inputs exist (`runs.config` and/or optional manifest).
- Surfaces **method-fidelity caveats** when run source or config warrants it.
- Adds **positional / needle** diagnostics only when **joinable metadata** exists.
- Keeps **latency** (per-request `latency_ms` in DB) linguistically separate from **batch throughput** (not a per-row field today).

Out of scope: Phase 1 doc cleanup (DOC-01/02), Phase 5 codebase map (DOC-03), new datasets, UI beyond markdown.

</domain>

<decisions>
## Implementation Decisions

### ANA-01 — Optional filtering (compression-aware + short-doc)

- **D-01:** Define a single optional object in **`runs.config`** (internal runs already store JSON config; imported runs store `run_metadata` as config): **`analysis_filters`**, with documented keys:
  - **`min_prompt_tokens`** (integer, optional): drop prediction rows with `prompt_tokens <` this before binning when the key is present.
  - **`max_prompt_tokens`** (integer, optional): symmetric upper bound when present.
  - **`compression_active_only`** (boolean, default false): when true, keep only rows that match a per-example signal **if available**; see D-02.
- **D-02:** Per-example **compression** signal: **no new SQLite column in the minimal plan** unless implementation proves necessary. Prefer **`contextcliff profile`** accepting an optional **`--manifest PATH`** that loads `Example.id` → `Example.metadata` (existing `formats.Example`). If `compression_active_only` is true and manifest is **missing**, the report must include an explicit **warning line** that the filter was requested but cannot be applied (no silent full run).
- **D-03:** CLI overrides: optional **`--min-prompt-tokens`** / **`--max-prompt-tokens`** on **`profile`** override `analysis_filters` for that invocation (document precedence: CLI > `runs.config`).

### ANA-02 — Method-fidelity caveats

- **D-04:** Add a markdown section **`## Caveats`** (or **`## Method notes`**) when **any** of: `run_source == 'imported'`, `artifact_ref` is non-null, or `runs.config` contains external-method keys (e.g. `method`, `compression_method`, `model` from imported metadata). Content is **templated prose** plus **dynamic** bullets from provenance (label, artifact ref, run source). **Imported runs always** get at least one caveat line stating that metrics reflect the **external** execution path, not in-repo API timing semantics.
- **D-05:** Do not imply numerical equivalence between internal and imported runs beyond what scores mean (F1/EM); avoid marketing language.

### ANA-03 — Positional / needle-in-haystack diagnostics

- **D-06:** When **`--manifest`** is provided and manifest examples include **documented optional metadata keys** (e.g. `needle_position`, `answer_position`, or quantile bucket — exact key names are **Claude’s discretion** but must be documented in implementation), compute aggregates **by bucket** (e.g. mean F1 by position quartile) and emit a subsection **`## Positional diagnostics`**. If manifest is absent or keys missing, **omit** the subsection and do **not** treat as error.
- **D-07:** If positional metadata is partially present, prefer **showing available buckets** over failing.

### ANA-04 — Latency vs throughput

- **D-08:** In **`## Executive Summary`** (or adjacent), add a short **Metrics interpretation** bullet block:
  - **`latency_ms`** is **per-request wall time** as recorded in SQLite (internal run) or imported artifact.
  - **Throughput** (examples/sec, batch sizing) is **not** stored per row; report must **not** present `latency_ms` averages as throughput. If `runs.config` documents batch size / total wall clock for an external run, allow an **optional** one-line note sourced from config only — never inferred by dividing counts by mean latency without user-provided totals.

### Reporting integration

- **D-09:** Keep **`CliffProfiler.generate_markdown_report`** as the primary report body; extend signature or pass a **structured “report extras”** dict so binning/filter summaries and caveats stay testable. **`ResultBinner`** remains the aggregation entry; filtering runs **before** `bin_results` when filters apply.
- **D-10:** Phase 3 provenance one-liner remains; **extend** with `artifact_ref` in the header line when non-null (ANA-02 alignment).

### Claude's Discretion

- Exact **`analysis_filters`** key names and manifest metadata key names (must be documented in code + short `docs/` or docstring table).
- Whether positional aggregation uses quartiles vs fixed bins.
- Helper module split (`analysis/filters.py` vs inline) if it keeps `binning.py` readable.
- Unit tests vs golden markdown snippets for reports.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap

- `.planning/REQUIREMENTS.md` — **ANA-01, ANA-02, ANA-03, ANA-04** (acceptance criteria for this phase).
- `.planning/ROADMAP.md` — Phase 4 goal and success criteria (filters/caveats/positional/latency wording).
- `.planning/PROJECT.md` — Active bullets on analysis lessons (compression filtering, caveats, positional, latency vs throughput).

### Prior phase contracts

- `.planning/phases/02-run-provenance-in-sqlite/02-CONTEXT.md` — `runs` provenance columns; internal vs imported.
- `.planning/phases/03-external-import-bridge/03-CONTEXT.md` — import boundaries; `run_metadata` → `runs.config`; minimal report line (Phase 4 enriches).

### Code integration points

- `src/contextcliff/analysis/binning.py` — `ResultBinner.load_run_data`, `bin_results`.
- `src/contextcliff/analysis/cliff.py` — `CliffProfiler.detect_cliff`, `generate_markdown_report`.
- `src/contextcliff/cli/main.py` — `profile` command wiring.
- `src/contextcliff/runner/state.py` — `get_run_provenance`, `runs.config` access patterns.
- `src/contextcliff/data/formats.py` — `Example.metadata` for manifest join semantics.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`CliffProfiler`**: cliff detection and markdown skeleton already exist; extend rather than fork.
- **`ResultBinner`**: loads `predictions` by `run_id` with parameterized SQL; natural place for optional row filters before `bin_results`.
- **`StateManager.get_run_provenance`**: already returns `run_source`, `external_label`, `artifact_ref`, `config`.

### Established Patterns

- Click options on CLI commands; default DB `state.db`.
- Pandas for binning; F1/std/failure rate columns already in markdown table.

### Integration Points

- **`profile` command** (`cli/main.py`): add optional `--manifest`, optional token thresholds; load provenance + parse `runs.config` for `analysis_filters`.
- **Manifest JSON** (from `prepare`): list of objects compatible with `Example` — join key `example_id` / `id`.

</code_context>

<specifics>
## Specific Ideas

- Align caveat tone with the **Omega reset** goal: honest about what imported vs internal runs measure.
- Prefer **warnings in the markdown** over silent behavior when a requested filter cannot be applied.

</specifics>

<deferred>
## Deferred Ideas

- Rich compare-UI or multi-run dashboards — out of scope for Omega reset.
- New SQLite columns for per-example compression flags — deferred unless manifest join proves insufficient.

### Reviewed Todos (not folded)

- None — `todo match-phase` returned no matches.

</deferred>

---

*Phase: 04-analysis-reporting*  
*Context gathered: 2026-03-27*
