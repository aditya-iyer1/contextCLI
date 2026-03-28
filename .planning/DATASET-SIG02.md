# SIG-02 — Alpha controlled synthetic dataset (design contract)

**Status:** Locked for planning — implementation must conform; empirical results belong in Phase 8+.  
**Dataset CLI slug:** `alpha_synthetic`  
**Spec version:** `sig02-v1` (bump metadata `synthetic_version` when this document’s normative rules change).

---

## Purpose

Provide **one** minimal synthetic extractive-QA corpus for Alpha such that **length and difficulty are designed**, not observed. Binning is **fixed by the generator** (designed bins), not **post-hoc quantiles** over arbitrary lengths.

---

## Task (single)

- **Extractive QA only:** the correct answer is always a **literal substring** of the context (exact match scoring per [`.planning/SIGNAL-SPEC-ALPHA-v1.1.md`](SIGNAL-SPEC-ALPHA-v1.1.md)).
- **Answer always present** in the context for every example — no abstention, no empty gold.

---

## Generator (single, seedable)

- **One** procedural generator module (see Phase 7 plan for path); **deterministic** given a documented **global seed** and CLI args (`prepare --dataset alpha_synthetic`, `--bins`, etc.).
- **No committed golden JSONL** in the initial implementation — add snapshots only if determinism is in doubt or tests need stable fixtures.

---

## Bins (designed, not quantile)

- **`--bins K`:** **K** fixed **designed** strata (e.g. increasing target length and/or burial depth per stratum).
- **Equal `n` per bin** by construction (same number of examples in each bin for a given run configuration).
- **No** assigning examples to bins by **quantiles of realized token lengths** on an observational stream — this is a **controlled** dataset, not NLDA-style sampling.

The existing [`balance_samples`](../src/contextcliff/data/sampler.py) **quantile** path applies to **`narrativeqa`** (and similar); the **`alpha_synthetic`** path must use **generator-defined bin indices** end-to-end.

---

## Difficulty knob — needle-offset (primary)

- **Primary knob:** **answer burial depth** — distance from the start of the context (or another fixed anchor) to the **needle** (the substring that must be copied as the answer). Higher bins increase burial **by design**.
- **Filler:** distractor text exists **only** to realize length and burial (padding before/around the needle as specified). Filler is not an independent “difficulty axis” for Alpha beyond supporting the needle-offset schedule.

Document concrete per-bin needle-offset (and filler) rules in the generator docstring or a short “Implementation notes” subsection when code lands.

---

## Monotonic length

- **Total context length** (tokens) grows **monotonically with bin index** \(k = 1 \ldots K\) **by construction** (short → long). The generator must enforce this; no reliance on stochastic length sorting after the fact.

---

## Metadata (per `Example`)

Minimum keys (names may match implementation but semantics are fixed):

| Key | Meaning |
|-----|---------|
| `synthetic_version` | e.g. `sig02-v1` |
| `alpha_bin` | Integer bin \(1 \ldots K\) (designed stratum) |
| `needle_offset` | (Recommended) token or char offset of answer span for diagnostics / profile join |

---

## Expected outcome (for Alpha validation)

**Not** a guarantee of model scores — a statement of **what the harness is built to detect**:

- As **`alpha_bin`** increases (longer contexts, deeper burial per this spec), **performance is not expected to improve** under a fixed model: mean **EM** should not systematically **increase** with \(k\) under the [SIG-01](SIGNAL-SPEC-ALPHA-v1.1.md) degradation notion (soft downward trend + statistical separation in later phases).
- If the controlled setup **fails** to show the expected directional pattern, **Alpha fails** per milestone rules — the harness does not “move the goalposts” by redefining bins post hoc.

---

## CLI / integration

- **No new commands** — only **`contextcliff prepare --dataset alpha_synthetic`** (and existing flags such as `--bins`) wired through [`cli/main.py`](../src/contextcliff/cli/main.py) and sampler dispatch.

---

## Completion gate

Phase 7 implementation is **not** complete until:

1. This document’s rules are satisfied by the shipped generator + adapter path, and  
2. A short **“Implementation summary”** paragraph is appended below (or linked PR) with actual seed constant name, **K**, **n per bin**, and tokenizer id — **without** changing the normative rules above without bumping `synthetic_version`.

### Implementation summary

*To be filled when SIG-02 code merges.*
