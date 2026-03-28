# Phase 7: Controlled dataset - Context

**Gathered:** 2026-03-28  
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver **SIG-02**: **one** minimal **controlled synthetic** QA dataset such that:

- **Ground-truth answers** are always defined (short strings; EM unambiguous per [`.planning/SIGNAL-SPEC-ALPHA-v1.1.md`](../../SIGNAL-SPEC-ALPHA-v1.1.md)).
- **Context length** increases **monotonically** across **length bins** (bin index \(k=1\ldots K\), short → long).
- **Answer burial / noise** increases **systematically** with bin (e.g., more distractor text, deeper needle placement, or both)—documented in the dataset spec.
- **Reproducible** build from repo (seeded generator and/or committed fixtures + one command path).
- **No new CLI commands** — extend existing **`contextcliff prepare --dataset …`** and [`balance_samples`](../../../src/contextcliff/data/sampler.py) routing only ([`cli/main.py`](../../../src/contextcliff/cli/main.py)).

Out of scope for Phase 7: API runs (**SIG-03**), bootstrap analysis (**SIG-04**), cliff implementation beyond what metadata must support for later phases, import/KV (**SIG-06**).

</domain>

<decisions>
## Implementation Decisions

### Dataset identity and wiring
- **D-01:** Register the dataset under CLI flag value **`alpha_synthetic`** (slug stable for scripts and docs). `prepare --dataset alpha_synthetic` selects the SIG-02 path; **`--bins`** continues to mean quantile-style bin count unless implementation fixes equal-count bins for synthetic (planner: choose **equal examples per bin** for Alpha control, or document quantile behavior if using variable synthetic lengths).
- **D-02:** Add **`AlphaSyntheticAdapter`** (or equivalent name) implementing [`BaseAdapter`](../../../src/contextcliff/data/adapters/base.py), yielding [`Example`](../../../src/contextcliff/data/formats.py) rows. Keep **`Example.id`**, **`context`**, **`question`**, **`answers`**, **`context_tokens`**, **`metadata`** populated; **tiktoken** counting aligned with [`NarrativeQAAdapter`](../../../src/contextcliff/data/adapters/narrative_qa.py) defaults (**`o200k_base`**, **`cl100k_base`** fallback) unless a one-line note in the dataset spec justifies a different encoder for Alpha only.
- **D-03:** Extend [`balance_samples`](../../../src/contextcliff/data/sampler.py) with `elif dataset_name == "alpha_synthetic":` (or dispatch map) — **no** parallel prepare pipeline.

### Content model (minimal, controlled)
- **D-04:** **Task:** extractive-style QA — the correct answer is a **literal substring** (or short span) of the context so **EM** matches human intent and scoring stays strict. One accepted answer string per example in **`answers`** (list of one element is fine).
- **D-05:** **Burial:** implement **systematic** difficulty increase with bin — e.g. fixed **needle sentence** containing the answer token(s), surrounded by growing filler paragraphs (repeated or templated distractor text), and/or increasing distance from context start to the needle. Exact scheme is **versioned** in metadata (`synthetic_version`, `alpha_bin`, optional `burial_depth` / `filler_tokens`).
- **D-06:** **Expected degradation (documented):** In [`.planning/DATASET-SIG02.md`](../../DATASET-SIG02.md) (or equivalent single file under `.planning/`), state explicitly: as **`alpha_bin`** increases (longer / more buried), **mean EM is not expected to improve** under fixed model behavior; separation will be tested in later phases per SIG-01. This satisfies roadmap success criterion #2 without pre-judging empirical results.

### Reproducibility
- **D-07:** **Seeded** procedural generation: global **`ALPHA_SIG02_SEED`** (constant in code or module-level, documented) so two runs produce the same **`manifest.json`** given same CLI args. Optionally add a **tiny** committed **golden** subset (JSONL) for unit tests.
- **D-08:** Do **not** rely on HuggingFace downloads for the primary SIG-02 path (keeps CI/offline reproducibility); HF optional only if deferred.

### Integration with downstream (Phase 8+)
- **D-09:** **`metadata`** must include at least **`alpha_bin`** (int) and **`synthetic_version`** so **`profile`** / manifest join can support positional notes ([Phase 4 patterns](../04-analysis-reporting/04-CONTEXT.md)) and filters without schema migrations in Phase 7.

### Claude's Discretion
- Filler text style (lorem vs repeated sentences), exact **K** and **n_per_bin**, and whether bins use **token targets** vs **quantiles** of generated lengths — chosen to meet D-04–D-06 and stay minimal.
- File layout: prefer **`src/contextcliff/data/adapters/alpha_synthetic.py`** + optional **`data/alpha_sig02_golden.jsonl`** only if tests need it.

### Folded Todos
- None (`todo match-phase 7` returned no matches).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Signal & milestone
- [`.planning/SIGNAL-SPEC-ALPHA-v1.1.md`](../../SIGNAL-SPEC-ALPHA-v1.1.md) — EM, bins, variance, degradation, **no alternate metrics** for Alpha primary signal.
- [`.planning/REQUIREMENTS.md`](../../REQUIREMENTS.md) — **SIG-02** acceptance text.
- [`.planning/ROADMAP.md`](../../ROADMAP.md) — Phase 7 success criteria (reproducible build, expected direction documented, prepare path).

### Prior phase context
- [`.planning/phases/06-signal-contract/06-CONTEXT.md`](../06-signal-contract/06-CONTEXT.md) — SIG-01 locks; dataset must not redefine cliffs or bootstrap.

### Dataset spec (to be added in Phase 7 implementation)
- [`.planning/DATASET-SIG02.md`](../../DATASET-SIG02.md) — **Create during execution** — burial scheme, bins, seed, expected degradation statement.

### Code
- [`.planning/phases/04-analysis-reporting/04-CONTEXT.md`](../04-analysis-reporting/04-CONTEXT.md) — manifest join / metadata for profile.
- [`src/contextcliff/data/formats.py`](../../../src/contextcliff/data/formats.py) — `Example`
- [`src/contextcliff/data/adapters/base.py`](../../../src/contextcliff/data/adapters/base.py)
- [`src/contextcliff/data/sampler.py`](../../../src/contextcliff/data/sampler.py)
- [`src/contextcliff/cli/main.py`](../../../src/contextcliff/cli/main.py) — `prepare`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets
- **`BaseAdapter` + `NarrativeQAAdapter`** — pattern for `load_stream()`, tokenization, `Example` construction.
- **`balance_samples`** — binning, merging sparse bins, manifest output path (extend dataset branch).
- **`prepare` command** — already exposes `--dataset` and `--bins`.

### Established patterns
- Token length via **tiktoken** on full `context` string (question embedded in context for NarrativeQA; SIG-02 may use same or a documented layout for consistent `context_tokens`).

### Integration points
- New adapter only; **Runner** / SQLite unchanged in Phase 7 unless a minimal metadata convention is already consumed from `Example` (verify in `runner/engine.py` if needed).

</code_context>

<specifics>
## Specific Ideas

- No interactive gray-area pass in this session: choices follow **ROADMAP** success criteria, **SIG-02** text, and **SIG-01** locked metrics. Revise via PR to `07-CONTEXT.md` if product intent shifts before `/gsd-plan-phase 7`.

</specifics>

<deferred>
## Deferred Ideas

- Multi-task or multi-hop variants — backlog, not SIG-02 minimal set.
- Using **NarrativeQA** as the Alpha dataset — **rejected** for SIG-02 (not controlled synthetic with known degradation direction).

### Reviewed Todos (not folded)
- None.

</deferred>

---

*Phase: 07-controlled-dataset*  
*Context gathered: 2026-03-28*
