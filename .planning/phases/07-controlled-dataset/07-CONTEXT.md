# Phase 7: Controlled dataset - Context

**Gathered:** 2026-03-28 (revised with explicit locks)  
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver **SIG-02**: **one** minimal **controlled synthetic** QA dataset such that:

- **Ground-truth answers** are always defined and **always present** in context (short strings; EM unambiguous per [`.planning/SIGNAL-SPEC-ALPHA-v1.1.md`](../../SIGNAL-SPEC-ALPHA-v1.1.md)).
- **Single task:** **extractive QA** only — no multi-task or alternate formulations in SIG-02.
- **Context length** grows **monotonically** with bin index **by generator construction** (not by sorting observed lengths).
- **Answer burial** increases **systematically** with bin; **needle-offset** is the **primary** difficulty knob; **filler** only realizes length/burial.
- **Reproducible:** **one** **seedable** generator; same CLI args → same manifest.
- **No new CLI commands** — extend **`contextcliff prepare --dataset alpha_synthetic`** and sampler dispatch only ([`cli/main.py`](../../../src/contextcliff/cli/main.py), [`sampler.py`](../../../src/contextcliff/data/sampler.py)).

**Design contract (normative, must exist before Phase 7 is “done”):** [`.planning/DATASET-SIG02.md`](../../DATASET-SIG02.md) — expected outcome and integration rules; implementation summary appended when code lands.

Out of scope for Phase 7: API runs (**SIG-03**), bootstrap analysis (**SIG-04**), golden JSONL fixtures unless determinism/testing demands them later.

</domain>

<decisions>
## Implementation Decisions

### Dataset identity and wiring
- **D-01:** CLI dataset slug **`alpha_synthetic`** — **locked**; no rename.
- **D-02:** Add **`AlphaSyntheticAdapter`** implementing [`BaseAdapter`](../../../src/contextcliff/data/adapters/base.py), yielding [`Example`](../../../src/contextcliff/data/formats.py). **tiktoken** defaults aligned with [`NarrativeQAAdapter`](../../../src/contextcliff/data/adapters/narrative_qa.py) unless **`DATASET-SIG02.md`** documents an Alpha-specific exception.
- **D-03:** Extend [`balance_samples`](../../../src/contextcliff/data/sampler.py) (or equivalent dispatch) for **`alpha_synthetic`** — **no** second prepare pipeline.

### Bins — designed, equal n, not quantiles
- **D-04:** **`--bins K`:** **K** **designed** strata from the generator. **Equal example count per bin** for a given run configuration.
- **D-05:** **No post-hoc quantile binning** for this dataset. The **generator** assigns each example’s **`alpha_bin`**; lengths are **controlled**, not sampled then split by quantiles (contrast with `narrativeqa` path in [`sampler.py`](../../../src/contextcliff/data/sampler.py)).

### Burial — needle-offset primary
- **D-06:** **Primary difficulty knob:** **burial depth / needle-offset** (distance from context anchor to the answer span). Increases monotonically with bin **by design**.
- **D-07:** **Filler** text exists **only** to support realized token length and the needle-offset schedule — not a separate competing difficulty axis.

### Task and answers
- **D-08:** **Extractive QA only:** answer string is a **literal substring** of the context; **`answers`** always non-empty; answer **always present** in context.
- **D-09:** **One** seedable generator module — deterministic given documented seed + args.

### Monotonicity
- **D-10:** **Monotonic length growth** with bin index **by construction** (generator-enforced ordering of total context size short → long).

### Fixtures
- **D-11:** **Procedural generation first** — **no** committed **golden JSONL** initially; add only if determinism is questionable or tests need stable snapshots.

### Documentation gate
- **D-12:** [`.planning/DATASET-SIG02.md`](../../DATASET-SIG02.md) is the **normative design contract**; **expected outcome** for Alpha is stated there. **Phase 7 is not complete** until that document matches the shipped behavior and the **Implementation summary** section is filled (seed name, **K**, **n** per bin, tokenizer).

### Integration with downstream (Phase 8+)
- **D-13:** **`metadata`** includes at least **`alpha_bin`**, **`synthetic_version`**, and **`needle_offset`** (recommended) for profile / positional diagnostics per [Phase 4 context](../04-analysis-reporting/04-CONTEXT.md).

### Claude's Discretion
- Exact filler templates, concrete per-bin offset schedules, and character vs token offset for **`needle_offset`** — must satisfy D-04–D-10 and **`DATASET-SIG02.md`**.

### Folded Todos
- None.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Signal & dataset (normative)
- [`.planning/SIGNAL-SPEC-ALPHA-v1.1.md`](../../SIGNAL-SPEC-ALPHA-v1.1.md) — EM, bins, degradation/cliff semantics for analysis phases.
- [`.planning/DATASET-SIG02.md`](../../DATASET-SIG02.md) — **SIG-02 design contract**, expected outcome, completion gate.

### Milestone
- [`.planning/REQUIREMENTS.md`](../../REQUIREMENTS.md) — **SIG-02**.
- [`.planning/ROADMAP.md`](../../ROADMAP.md) — Phase 7.

### Prior phase
- [`.planning/phases/06-signal-contract/06-CONTEXT.md`](../06-signal-contract/06-CONTEXT.md) — SIG-01 locks.

### Code
- [`.planning/phases/04-analysis-reporting/04-CONTEXT.md`](../04-analysis-reporting/04-CONTEXT.md) — manifest/metadata join.
- [`src/contextcliff/data/formats.py`](../../../src/contextcliff/data/formats.py) — `Example`
- [`src/contextcliff/data/adapters/base.py`](../../../src/contextcliff/data/adapters/base.py)
- [`src/contextcliff/data/sampler.py`](../../../src/contextcliff/data/sampler.py)
- [`src/contextcliff/cli/main.py`](../../../src/contextcliff/cli/main.py)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets
- **`BaseAdapter`** / **`NarrativeQAAdapter`** — streaming `Example` pattern.
- **`prepare`** — `--dataset` / `--bins` flags.
- **`balance_samples`** — today implements **quantile** binning for **narrativeqa**; **`alpha_synthetic`** needs a **separate branch** that consumes **generator-defined** bins and **equal n**, not quantile reassignment.

### Integration points
- New adapter + sampler branch; Runner unchanged unless metadata consumption is verified.

</code_context>

<specifics>
## Specific Ideas (user-locked 2026-03-28)

1. **Slug:** `alpha_synthetic` — keep.  
2. **Bins:** equal **n** per bin; **designed** by generator — **not** post-hoc quantiles.  
3. **Burial:** **needle-offset** emphasis; filler supports the knob.  
4. **Fixtures:** procedural first; golden JSONL only if needed.  
5. **Additional locks:** answer always present; one task (extractive QA); one seedable generator; monotonic length by construction; **`DATASET-SIG02.md`** complete before Phase 7 implementation is considered done.

</specifics>

<deferred>
## Deferred Ideas

- Golden JSONL snapshots — only if determinism or testing requires.
- Multi-task / NarrativeQA-as-Alpha — out of scope for SIG-02.

### Reviewed Todos (not folded)
- None.

</deferred>

---

*Phase: 07-controlled-dataset*  
*Context gathered: 2026-03-28 — revised with explicit bin/burial/fixture locks*
