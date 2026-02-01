# Overview

Measuring the effective reasoning limit of an LLM by evaluating naturally long examples across length bins, treating varaince spikes as first-class signals (the "cliff"), not noise.

# Motivations

Lots of long-context evidence is consistent with the hypothesis that "advertised context length $\ne$ reliable reasoning length":
* **Position Sensitivity**: Performance often peaks when relevant evidence is near the beginning/end, and drops when it's in the middle (lost in the middle)
* Benchmarks showing "real context size" can be much smaller than claimed when tasks go beyond trivial recall
* Broader benchmark work indicates models still struggle as length increases, and that retrieval/compression only partially closes the gap.

This doesn't prove cliffs *always* 

# Primary Method Commitments/Guardrails

## Natural Length Distribution (NLDA)

* No truncation, padding, synthetic neddle inserts
* Each sample is evaluated at native length
* Group samples into length bins (quantiles or fixed-width range tokens)
* Report mean + variance + instability per bin

## Black-box, deterministic evaluation
* No activations, no fine-tuning, no LLM-as-judge (unless later justified)
* Prefer **Exact Match / token-f1 / execution success** (depending on task)
* Fix randomness: temperature 0; consistent formatting, robust parsing

## Variance as signal (not noise)
* Treat a "transition region" as increased variance / bimodaility / failure volatility
* The "safe context cap" is a conservative cutoff before volatility explodes

# End-to-end conceptual pipeline

## Stage 0: Defining the Objective

**Goal**: "Effective reasoning limit" for a specific task type (e.g., long-doc QA)

### Decision Points:
* **Task Family**: QA (NarrativeQA), multi-doc QA, summarization, coreference, etc.
* **Metric**: EM/F1 (QA), ROUGE (iffy), exact structured output match, etc.
* **Model access mode**: API vs local; single model vs comparing multiple

### Guardrails:
* Don't interpret results as "model ranking overall" — it's *task condition reliability*

## Stage 1: Dataset Curation with Natural Length Distribution

### Goal: Get a dataset where length varies widely *without manufacturing it*.

### What I store per example:
* `id`
* `context` (raw document)
* `question`
* `answer` (ground truth)
* `length_tokens_context`
* optional: metadata like domain/topic/source/length

### Decision Points:
* Filtering: removing extremely short contexts (no long-context signal)
* Handling multiple references / acceptable answers
* Cost-aware sampling (Likely not able to run full dataset)

## Stage 2 — Prompting & response normalization

### Goal: keep prompting constant so length is the independent variable.

### Prompt template principles
* Minimal instructions; stable format; deterministic output.
* Hard constraint: “Answer with only the final answer string.”

### Normalization
* Lowercasing, punctuation stripping, article removal (optional)
* For F1: tokenize consistently (SQuAD-style tokenization)

### Guardrails
* Avoid adding “helpful” scaffolding that changes with context length.
* Keep output format stable across all bins.

## Stage 3 — Binning strategy (the spine of ContextCliff)

### Goal: partition by natural context lengths.

### Recommended default
* Quantile bins (e.g., deciles): more stable sample counts per bin.
* Track each bin’s [min_tokens, median_tokens, max_tokens, n].

### Alternative
* Fixed-width bins (e.g., 0–8k, 8–16k…): easier to interpret in tokens but can be sparse in the tail.

### Guardrails
* Ensure each bin has enough samples for variance estimates (even if rough).
* If tails are sparse, merge top bins rather than hallucinating conclusions.

## Stage 4 — Evaluation run (deterministic)

### Goal: run the model on each sample; capture outputs + telemetry.

### Record everything
* raw prompt
* raw model output
* parsed answer
* EM / F1
* token usage (prompt + completion)
* runtime
* any parse failures

### Guardrails
* “Invalid output” is a failure mode—track it as such.
* Keep retries off by default; if you do retries, log them.


## Stage 5 — Cliff detection (mean + variance + instability)

This is where your project becomes ContextCliff instead of “another benchmark run.”

### Per bin compute
* *mean_score
* std_score / var_score
* failure_rate (EM==0 or parse fail)
* instability: e.g.,
* bootstrap CI width for mean
* rolling variance
* mixture/bimodality indicators (optional, later)

### Cliff heuristics (v1)
* Transition starts when variance or failure-rate rises sharply relative to previous bins.
* Degraded region when mean collapses and failure-rate stays high.
* Safe context cap = the highest bin edge before transition (conservative).

### Guardrails
* Don’t overfit “cliff thresholds.” Start with transparent heuristics + sensitivity checks.
* Always show uncertainty (CI bands, bootstrap).

## Stage 6 — Output artifact: Context Failure Profile

### Deliverable: a machine-readable + human-readable report:
* Stable region: bins where mean stable + variance low
* Transition: high variance / volatile outcomes
* Degraded: persistently low mean + high failure
* Recommended safe cap: token threshold


Additional key focuses:

The provided documentation offers a strong foundation for **ContextCliff**. While `architecture.md` was empty, the project’s structure is well-defined across the `overview.md`, `prd.md`, and `critique.md` files.

Based on these documents and the core methodology of **Natural Length Distribution Analysis (NLDA)**, here is an evaluation and refined proposal for your project architecture.

### 1. Data Layer: The "Natural Length" Guard

The primary risk in this layer is **Data Scarcity** in long-context bins. Since you are not truncating or padding, you are at the mercy of the dataset's inherent distribution.

* **Refinement:** Implement a **Distribution Auditor**. Before running inference, this module should scan your dataset (e.g., NarrativeQA) and generate a histogram of token counts.
* **Replacement Suggestion:** Instead of just "Dataset Adapters," use a **Bin-Aware Sampler**. If a specific bin (e.g., 50k–60k tokens) has only 2 samples, the tool should flag this as "Statistically Insignificant" or automatically merge it with an adjacent bin to maintain signal integrity.

### 2. Runner Layer: Deterministic Execution

To meet your "Solo-Engineer" and "Cost-Aware" constraints, this layer must be highly resilient to network failures and API costs.

* **Fix:** Add a **Cost-Governor**. This module should calculate the estimated cost of a "Run" based on the total tokens in the selected bins before sending requests to the API.
* **In-depth Detail:** * **State Management:** Use a local database (like SQLite) to track every request. If the CLI crashes, it should resume from the last successful token bin without re-processing.
* **Prompt Sanitization:** Ensure the "Natural Length" remains natural by using a minimal, stable scaffold that does not add significant token overhead or change across bins.



### 3. Metric Layer: Failure Taxonomy

Moving beyond simple EM/F1 is what will provide the "Scientific Rigor" you seek.

* **New Module: Failure Mode Classifier.** Instead of just recording a "0" for a wrong answer, categorize the failure:
* **Format Failure:** Model failed to follow the output schema (a common sign of context pressure).
* **Hallucination:** Model provided an answer not present in the text.
* **Incompleteness:** Model stopped mid-sentence (often due to context window limits).


* **Justification:** High variance in the "Transition Region" is often caused by a mix of correct answers and "Format Failures".

### 4. Profiler Layer: The "Cliff" Detection Logic

This is the "brain" of ContextCliff. It transforms raw scores into the **Context Failure Profile**.

* **Logic Fix:** The "Cliff" should not be defined by a mean score alone.
* **Replacement:** Use **Variance Spikes** as the primary signal. If the standard deviation of performance in Bin B is >2x the standard deviation in Bin A (the baseline), you have entered the **Transition Zone**.
* **Signal Detection:** Research suggests "Intelligence Degradation" is often catastrophic (dropping >30%) rather than linear. Your profiler should look for this specific non-linear drop-off point.

### 5. Report Layer: Actionable Engineering Artifacts

The output must be something an engineer can use for deployment decisions.

* **Visual Plot Requirements:**
* **X-axis:** Natural Context Length (Tokens).
* **Y-axis:** Performance (Primary) + Variance (Secondary, e.g., error bars).
* **Markers:** Explicitly label the **"Safe Operating Cap"**—the maximum token count before variance exceeds a predefined "Stability Threshold".


* **Machine-Readable Export:** A JSON file containing the `[min, median, max]` tokens and `n_samples` for every bin to ensure the results are reproducible.

### Recommended Architecture Overview

| Module | Responsibility | Key Signal/Guardrail |
| --- | --- | --- |
| **Data Auditor** | Scan dataset for natural lengths | Rejects bins with `n < [Threshold]` |
| **Resilient Runner** | API calling + State caching | Cost-governor + Resume capability |
| **Deterministic Evaluator** | EM/F1 + Format Validation | Categorizes "Invalid Output" as a failure |
| **Cliff Engine** | Statistical bin analysis | Identifies Variance Spikes & Collapse |
| **Profiler UI** | Generate JSON & Visual Plots | Defines "Safe Cap" for production |

### Follow-up Questions for Refinement:

1. **Budget Constraint:** What is your specific "per-model" budget? (e.g., Is <$50 per curve a hard limit?) This determines how aggressively the **Bin-Aware Sampler** needs to work.
2. **Model Selection:** Are you planning to test specific "frontier" models (like GPT-4o) or "open-weights" models (like Qwen2.5) via API providers?
3. **Stability Definition:** What constitutes an "unacceptable" variance spike for your use case? (e.g., A 10% increase in standard deviation or a specific drop in the 10th percentile of scores?)