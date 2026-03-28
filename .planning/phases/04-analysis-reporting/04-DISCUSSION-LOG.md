# Phase 4: Analysis & reporting — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.  
> Decisions are captured in `04-CONTEXT.md`.

**Date:** 2026-03-27  
**Phase:** 4 — Analysis & reporting  
**Areas discussed:** ANA-01 filtering, ANA-02 caveats, ANA-03 positional, ANA-04 latency vs throughput, integration (requirement-driven session)

---

## Session mode

Interactive gray-area multi-select was not completed in a back-and-forth thread. Context was produced by mapping **`.planning/REQUIREMENTS.md` (ANA-01–ANA-04)** and **`.planning/PROJECT.md` Active bullets** onto the current codebase (`binning.py`, `cliff.py`, `profile` CLI), using **recommended defaults** that satisfy the written requirements. **Edit `04-CONTEXT.md` before `/gsd-plan-phase 4` if any decision should change.**

---

## ANA-01 — Optional filtering

| Option | Description | Selected |
|--------|-------------|----------|
| A | Config-only `analysis_filters` in `runs.config` | ✓ |
| B | New SQLite columns per prediction for every filter | |
| C | Filters only via CLI, no config | |

**User's choice:** A (documented in CONTEXT as D-01–D-03)  
**Notes:** Short-doc suppression via `min_prompt_tokens` / `max_prompt_tokens`; compression-related filtering prefers manifest join when per-example data is required; warn if filter requested but manifest missing.

---

## ANA-02 — Caveats

| Option | Description | Selected |
|--------|-------------|----------|
| A | Dedicated `## Caveats` / method notes when imported or metadata present | ✓ |
| B | Caveats only in CLI stderr | |

**User's choice:** A (D-04–D-05)

---

## ANA-03 — Positional diagnostics

| Option | Description | Selected |
|--------|-------------|----------|
| A | Optional `--manifest` join + metadata keys; subsection only when data exists | ✓ |
| B | Schema migration to store position in SQLite | (deferred) |

**User's choice:** A (D-06–D-07)

---

## ANA-04 — Latency vs throughput

| Option | Description | Selected |
|--------|-------------|----------|
| A | Explicit markdown interpretation: `latency_ms` per-request; do not conflate with throughput | ✓ |
| B | Compute pseudo-throughput from mean latency | |

**User's choice:** A (D-08); optional config-sourced batch notes only when user provides totals in config.

---

## Claude's Discretion

- Exact manifest metadata key names for positional buckets.  
- Module layout for filter helpers.

## Deferred Ideas

- Per-example compression flags in SQLite — deferred (see CONTEXT `<deferred>`).
