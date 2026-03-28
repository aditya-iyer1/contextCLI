# Phase 6: Signal contract - Context

**Gathered:** 2026-03-27  
**Status:** Ready for planning

<domain>
## Phase Boundary

**Delivered:** Canonical **SIG-01** signal specification is **locked** in [`.planning/SIGNAL-SPEC-ALPHA-v1.1.md`](../../SIGNAL-SPEC-ALPHA-v1.1.md). Phase 6 does **not** add dataset, CLI, or analysis code; it establishes definitions **L1–L3** and all formulas downstream work must implement without reinterpretation.

**In scope for planning this phase (if a plan is written):** Trace requirements to the spec; add checklist/tests that code matches §§1–8; optionally document where **B**, **α**, and bootstrap **pairing** will be fixed at first execution (§8).

**Out of scope:** Implementing bootstrap, runs, or reports (Phases 7–12).
</domain>

<decisions>
## Implementation Decisions

### Canonical source of truth
- **D-01:** The **only** normative definition of variance, degradation, cliffs, metrics, and real-effect rules for Alpha is [`.planning/SIGNAL-SPEC-ALPHA-v1.1.md`](../../SIGNAL-SPEC-ALPHA-v1.1.md). Do not duplicate competing definitions in README or ad hoc comments; link to this file.
- **D-02:** Immutable milestone decisions **L1** (degradation), **L2** (Δ(score) cliff), **L3** (bootstrap with global **B**) must not be “reinterpreted” in implementation; if code cannot match the spec, fix code or escalate—do not silently change the math.

### Parameters deferred to first execution (§8)
- **D-03:** **B** (bootstrap resample count) and **α** (CI level) are **not** numerically fixed in Phase 6. They are fixed **once** when analysis first runs and stay constant for all Alpha artifacts thereafter.
- **D-04:** **Default for planning:** **α = 0.05** (two-sided CIs for bin means and for **Δ_k**), unless a later explicit amendment to the spec changes it. Document chosen **α** in run metadata when execution starts.
- **D-05:** Bootstrap **pairing** for **Δ_k** (how resamples are drawn for adjacent bins) is **one** algorithm chosen at implementation time and used for every boundary; spec requires a single protocol—**recommended default:** resample **within each bin independently** (same **B** per bin), compute **Δ̂_k** on each replicate pair; build CI from the distribution of **Δ̂_k***. (Planner/researcher may substitute an equivalent documented paired scheme if it matches the spec’s stability clauses—must be justified in PLAN.md.)

### Score and metrics
- **D-06:** Primary task score for Alpha is **EM** in \([0,1]\) per [`.planning/SIGNAL-SPEC-ALPHA-v1.1.md`](../../SIGNAL-SPEC-ALPHA-v1.1.md) § header; aligns with existing [`src/contextcliff/eval/metrics.py`](../../../src/contextcliff/eval/metrics.py).

### Integration targets (later phases, not Phase 6 code)
- **D-07:** When implemented, bin-level and cliff statistics should extend existing **`ResultBinner`** ([`analysis/binning.py`](../../../src/contextcliff/analysis/binning.py)) and **`CliffProfiler`** ([`analysis/cliff.py`](../../../src/contextcliff/analysis/cliff.py)) / **`profile_report`** ([`analysis/profile_report.py`](../../../src/contextcliff/analysis/profile_report.py)) rather than a parallel pipeline—**no new CLI** (Omega/Alpha contract).

### Claude's Discretion
- Exact bootstrap implementation details (seed handling, edge cases for **n_k < 2**) where the spec does not prescribe—must still satisfy §§3–6 (CI excludes 0, majority sign stability, reproducibility).
- Formatting of the eventual Alpha report (Phase 12) outside what SIG-07 requires.

### Folded Todos
- None (todo match for phase 6 returned no matches).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Signal specification (primary)
- [`.planning/SIGNAL-SPEC-ALPHA-v1.1.md`](../../SIGNAL-SPEC-ALPHA-v1.1.md) — Locked definitions: variance §1, degradation §2, cliff §3, metrics §4, statistics §5, real effect §6, parameters §8.

### Milestone & requirements
- [`.planning/PROJECT.md`](../../PROJECT.md) — v1.1 goals, hard constraints (no new CLI, API/mock only).
- [`.planning/REQUIREMENTS.md`](../../REQUIREMENTS.md) — SIG-01 through SIG-08.
- [`.planning/ROADMAP.md`](../../ROADMAP.md) — Phase 6 goal and dependency on locked spec.

### Prior phase context (analysis integration patterns)
- [`.planning/phases/04-analysis-reporting/04-CONTEXT.md`](../04-analysis-reporting/04-CONTEXT.md) — Reporting, `CliffProfiler`, caveats patterns from Omega.

### Code entry points (for planner scoping later phases)
- [`src/contextcliff/analysis/binning.py`](../../../src/contextcliff/analysis/binning.py) — `ResultBinner`
- [`src/contextcliff/analysis/cliff.py`](../../../src/contextcliff/analysis/cliff.py) — `CliffProfiler`
- [`src/contextcliff/analysis/profile_report.py`](../../../src/contextcliff/analysis/profile_report.py) — profile markdown
- [`src/contextcliff/eval/metrics.py`](../../../src/contextcliff/eval/metrics.py) — EM / F1

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`ResultBinner`** — Aggregates results by length bin; natural place to attach per-bin means and within-bin variance (SIG spec §1.1).
- **`CliffProfiler`** — Existing cliff-oriented reporting; extend to match **Δ_k** and bootstrap-backed rules in §3 (replacing or augmenting heuristics only as required by spec—planner decides minimal diff).
- **`profile_report`** — Markdown output path for Alpha report (SIG-07).

### Established Patterns
- Analysis reads **SQLite** via binner; CLI **`profile`** command wires binner + profiler ([`cli/main.py`](../../../src/contextcliff/cli/main.py)).
- Metrics centralized in **`eval/metrics.py`**.

### Integration Points
- No code changes in Phase 6 definition work; future implementation connects **bin aggregates** → **bootstrap** → **CI / Δ_k / cliff flags** → **profile report** without new user-facing commands.

</code_context>

<specifics>
## Specific Ideas

- User pre-locked Phase 6 via [`.planning/SIGNAL-SPEC-ALPHA-v1.1.md`](../../SIGNAL-SPEC-ALPHA-v1.1.md) before this discuss-phase; interactive gray-area selection was unnecessary because definitions are already exhaustive for Alpha.

</specifics>

<deferred>
## Deferred Ideas

- **DOC-01 / DOC-02 / RUN-01** — Remain conditional per `REQUIREMENTS.md`; not part of Phase 6 unless blocking interpretation.

### Reviewed Todos (not folded)
- None.

None — discussion stayed within phase scope

</deferred>

---

*Phase: 06-signal-contract*  
*Context gathered: 2026-03-27*
