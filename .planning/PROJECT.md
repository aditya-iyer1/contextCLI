# ContextCliff

## What This Is

**ContextCliff** is a Python CLI and SQLite-backed harness for **long-context degradation analysis**: sample or fix eval cases by natural length, run models via **API-style execution only**, score predictions, bin results by length, and report “cliff” behavior (where QA quality or stability falls off). This milestone is a **brownfield architecture reset**: restore the repo as a **reusable evaluation harness** and add a **clean import path** for KV-compression and other experiments executed **outside** this repository—without pretending those runs used the same in-process runtime as API calls.

## Core Value

**Trustworthy, comparable long-context evals**: one manifest, one scoring and analysis pipeline, SQLite as the canonical store—**API execution in-repo**, **external compression artifacts imported and explicitly labeled**—so conclusions are not mixed across incompatible execution models.

## Requirements

### Validated

Existing codebase capabilities (see `.planning/codebase/ARCHITECTURE.md`, `STACK.md`):

- ✓ **CLI pipeline** — `prepare` → `run` → `import` → `profile` (`src/contextcliff/cli/main.py`): manifest generation, batched inference, JSON artifact import, markdown cliff reports.
- ✓ **SQLite experiment store** — predictions and metrics in `state.db` via `StateManager` (`src/contextcliff/runner/state.py`); resume by skipping completed example IDs.
- ✓ **API-path execution** — `OpenAIClient` + `ModelClient` abstraction (`src/contextcliff/models/`); `mock` model for dry runs (`src/contextcliff/runner/engine.py`).
- ✓ **Scoring** — token F1 and exact match, best-over-gold-answers (`src/contextcliff/eval/metrics.py`).
- ✓ **Failure taxonomy** — `EvalRecord.failure_type` set on errors (e.g. context length, rate limit) in `Runner.run`.
- ✓ **Analysis & report** — length binning (`analysis/binning.py`), cliff heuristics and markdown report (`analysis/cliff.py`).
- ✓ **Data layer** — HF NarrativeQA adapter, NLDA-style quantile sampling (`data/sampler.py`, `data/adapters/narrative_qa.py`).
- ✓ **Run provenance (STA-01)** — `runs.run_source` / `external_label` / `artifact_ref`, migration + backfill, internal registration in `Runner.run()` (`Phase 2`, 2026-03-28).
- ✓ **Import bridge (IMP-01)** — `contextcliff import` + JSON `schema_version` 1, `import_external_run`, collision rules vs internal runs, minimal provenance line in cliff report (`Phase 3`, 2026-03-28).
- ✓ **Analysis & reporting (ANA-01–ANA-04)** — optional `analysis_filters` + manifest join on `profile`, caveats and metrics interpretation in markdown reports (`Phase 4`, 2026-03-28).

### Active

Architecture reset and harness clarity (this milestone):

- [ ] **Remove or deprecate misleading KV-runtime story** — docs (and any stray config) that imply in-repo SnapKV / PyramidKV / KVCache-Factory execution or fake `--kv_budget` on API backends; align README/docs with **API-only** execution in this repo.
- [ ] **Relock runner to engine-agnostic API execution** — single clear path: manifest → `ModelClient.generate` → metrics → SQLite; no mixed “local compression runtime vs API” equivalence claims in code paths.
- [x] **External artifact import bridge** — satisfied by Phase 3 (`import` CLI + SQLite `imported` rows + report header); further UX belongs in later phases.
- [x] **Preserve analysis lessons from the KV study** in analysis/reporting — satisfied by Phase 4 (`profile_report.py`, extended `CliffProfiler` reports).

### Out of Scope

- Full native **KVCache-Factory** (or similar) integration inside this repo.
- Redesigning around **multi-repo runtime orchestration** (this repo stays the harness + import sink).
- **Presentation polish** beyond what’s needed for clarity of the reset.
- **Broad productization** beyond reset + import + analysis integration.

## Context

- **Brownfield**: Codebase map lives under `.planning/codebase/`. Prior design docs (`docs/full_desc.md`, `docs/blueprint.md`, etc.) describe aspirational local/vLLM/KV-policy CLIs; **implementation in `src/` is currently API-centric**—reset work is partly **documentation and contract alignment**, partly **import + analysis**.
- **Constraint**: No mixed architecture where some runs are local monkeypatched compression and others are API calls presented as the same experiment type without labeling.

## Constraints

- **Execution**: Native paths remain **API / endpoint-based** only inside this repository; heavy KV work runs elsewhere and enters via **import**.
- **Honesty**: No request-time `kv_budget`-style controls on backends that do not support them.
- **Storage**: **SQLite** remains the canonical store for in-harness and imported runs (schema may extend for provenance).

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| API-only in-repo; KV experiments external + import | Avoid false equivalence and unsupported runtime surface | — Pending |
| Imported runs explicitly labeled | Prevents mixing external and in-process semantics | — Pending |
| Keep prepare → run → score → analyze → report structure | Preserves reusable harness mental model | — Pending |

## Milestone: Architecture reset — plan and execution order

**Goal:** Deliver the Active requirements above with minimal churn: align docs with `src/`, add import bridge, extend analysis without breaking existing API runs.

**Suggested file-by-file / area order** (dependencies first):

1. **`src/contextcliff/` contract** — Confirm `ModelClient`, `Runner`, `formats` datatypes; document what “run” means (API-only). Adjust naming/comments only if needed for clarity.
2. **`src/contextcliff/runner/state.py`** — Design/implement schema fields (or parallel table) for **run provenance**: e.g. `source=internal|imported`, external labels, link to artifact manifest. Migrate safely for existing DBs.
3. **Import bridge** — New module (e.g. `contextcliff/import_/` or `runner/import_bridge.py`) + **CLI entry** (e.g. `contextcliff import` or flags on `run`) to load external artifacts into SQLite with mandatory metadata.
4. **`src/contextcliff/analysis/`** — Integrate filtering (compression-active, short-doc suppression), caveats, positional/needle diagnostics, latency vs throughput wording in `CliffProfiler` / reporting helpers as appropriate.
5. **`src/contextcliff/cli/main.py`** — Wire import command; remove or gate any misleading options if introduced later.
6. **Docs cleanup** — `docs/full_desc.md`, `docs/blueprint.md`, `docs/architecture_preview.md`, `docs/data_layer.md`: strike or mark **deprecated** the vLLM/`--kv_policy` “as-built” narrative; point to **import path** for compression studies. Update `.planning/codebase/*` after code stabilizes.
7. **`pyproject.toml` / deps** — Add missing declared deps (e.g. `python-dotenv`) if touched; avoid new heavy runtime deps for KV execution.

**Not ordered strictly:** root scripts (`dry_run.sh`, `test.py`) and ad hoc tools—update after core path works.

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):

1. Requirements invalidated? → Move to Out of Scope with reason  
2. Requirements validated? → Move to Validated with phase reference  
3. New requirements emerged? → Add to Active  
4. Decisions to log? → Add to Key Decisions  
5. “What This Is” still accurate? → Update if drifted  

**After each milestone** (via `/gsd-complete-milestone`):

1. Full review of all sections  
2. Core Value check — still the right priority?  
3. Audit Out of Scope — reasons still valid?  
4. Update Context with current state  

---
*Last updated: 2026-03-28 — Phase 3 (IMP-01) validated; Validated / Active updated.*
