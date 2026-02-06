# Data Layer

## Conceptual Outline

The Data Layer is the immutable foundation of the **Natural Length Distribution Analysis (NLDA)**. Its primary directive is to source, normalize, and stratify evaluation samples without introducing the "truncation artifacts" that plague standard benchmarks. It functions as a strict **Bin-Aware Pipeline** that converts raw, chaotic datasets into a deterministic execution manifest.

**Core Philosophy:**
To measure the "Cliff" (the specific token count where reasoning fractures), the data must inherently exist at that length. We do not pad short documents (which distorts attention density) nor truncate long documents (which breaks reasoning chains).

**End-to-End Workflow:**

1. **Ingestion & Normalization:**
   The layer accepts diverse inputs—huggingface datasets (NarrativeQA, SQuAD), local binaries (PDFs), or raw text. Adapters normalize these into a rigorous `EvalCase` schema, stripping away dataset-specific quirks while preserving the full, raw context.
2. **Distribution Auditing (The "Scan"):**
   Before any selection occurs, the **Distribution Auditor** tokenizes a massive buffer (e.g., ) of potential candidates. It computes the "Natural Length Histogram" to visualize the available density across the 1k–128k+ spectrum.
3. **Stratified Quantile Binning:**
   Unlike random sampling, this engine performs **Inverse-Density Sampling**. It divides the target context window into stratified bins (e.g., Deciles: 0-10%, 10-20%... of max length) and fills each bin with a fixed samples (e.g., ). This ensures the "Long Tail" (100k+ tokens) has equal statistical weight to the "Short Head" (4k tokens).
4. **Manifest Generation:**
   The final output is a static `manifest.json`. This file is the **Contract of Execution**. It contains the exact content and metadata for the run. Once generated, the Runner Layer (Phase 2) reads strictly from this manifest, ensuring that Baseline Runs and KV-Cache Compression Runs evaluate the exact same text samples.

---

## Architecture

This architecture enforces the **Separation of Concerns** principle: The Data Layer knows nothing about models, APIs, or KV caches. It only knows about text, tokens, and structure.

### `data/formats.py`

**Role:** The "Source of Truth" for data contracts.

- **`EvalCase` (Pydantic Model):** The atomic unit of evaluation.
- `id`: unique hash (prevents duplicates).
- `context`: Full, untruncated text.
- `question`: The query requiring reasoning.
- `answers`: List of valid gold-standard answers (for Exact Match/F1).
- `meta`: Dictionary containing `token_count`, `source_dataset`, and `difficulty_tier`.

- **`Manifest`:** The container object that serializes the list of `EvalCase` items to JSON.

### `data/adapters.py`

**Role:** The Translation Layer. Converts external formats into `EvalCase`.

- **`BaseAdapter`:** Abstract interface requiring `load()` and `normalize()` methods.
- **`NarrativeQAdapter`:** Handles the complexity of mapping NarrativeQA's `summary` vs `full_text`. _Crucial:_ Filters out samples where the answer relies solely on the summary, ensuring the model _must_ read the book (Long Context necessity).
- **`SQuADAdapter`:** Ingests SQuAD v2.0 to populate the "Short Context" bins (1k–10k), providing the high-fidelity baseline required to calculate the degradation slope.
- **`LocalFileAdapter`:** Parses user-uploaded `.md` or `.txt` files, enabling "Bring Your Own Data" (BYOD) for proprietary cliff testing.

### `data/sampler.py`

**Role:** The "Bin-Aware" Engine.

- **`scan_distribution(source, buffer_size)`:** Lazily loads and tokenizes thousands of examples using `tiktoken` (efficient BPE tokenization) to build the population map.
- **`stratify_and_select(strategy='quantile', k_samples=20)`:**
- Sorts the scanned population by length.
- Partitions into bins.
- Selects samples from each bin.
- _Logic:_ If Bin 9 (80k-100k) has only 5 samples, it takes all 5 and flags a warning, rather than duplicating or padding.

### `data/distribution.py`

**Role:** Feasibility Analysis & Reporting.

- **`DistributionAuditor`:** A standalone utility that outputs a histogram (CLI visual) of the raw data.
- **`check_feasibility(model_limit)`:** Validates if the generated manifest is compatible with the target model.
- _Example:_ If the user targets `Llama-3-8B` (8k limit) but the manifest contains 100k-token samples, this module halts execution _before_ expensive API calls or OOM errors occur.

---

## Tradeoffs & Guardrails

### 1. The "Natural Length" Tradeoff

- **Decision:** **Strict NLDA (No Truncation, No Padding).**
- **The Tradeoff:** We accept **Data Scarcity** in the tails. finding 50 distinct documents naturally between 125k–128k tokens is difficult.
- **The Gain:** **Causal Validity.** When performance drops, we know it is due to _length_, not because we chopped off the reasoning chain (truncation) or diluted attention with `<pad>` tokens.
- **Guardrail:** **Dynamic Bin Merging.** If high-end bins are too sparse (), `sampler.py` automatically merges them (e.g., merging Decile 9 and 10) to maintain statistical significance, notifying the user via `stderr`.

### 2. Mixed-Source Stratification

- **Decision:** **Hybrid Dataset Injection.**
- **The Friction:** NarrativeQA is excellent for 20k–100k, but sparse in the <10k region. SQuAD is excellent for <10k but nonexistent for long context.
- **The Solution:** The `Sampler` treats sources as a "Pool." It fills the 0-10% bin primarily with SQuAD and the 20-100% bins with NarrativeQA.
- **Guardrail:** **Source Tracking Metadata.** The `EvalCase.meta` field tracks the `origin`. The Analysis Layer (Phase 3) must account for this shift so we don't mistake a change in _dataset difficulty_ for a change in _model performance_.

### 3. KV Cache Agnosticism

- **Decision:** **Raw Text Delivery.**
- **The Logic:** The Data Layer does **not** simulate KV compression (H2O, SnapKV). It delivers the full text.
- **Why:** To measure the "Delta" (the shift in the cliff), the _exact same_ `manifest.json` must be run twice:

1. **Baseline Run:** Full Attention.
2. **Experimental Run:** Compressed KV Cache (Runner Layer applies the policy).

- **Guardrail:** **Deterministic Hashing.** Each `EvalCase` has a content-based hash. The Runner verifies that the input text for the Compressed Run matches the Baseline Run bit-for-bit before applying compression.

### 4. User Inputs & Variables

- `--dataset`: `narrativeqa`, `squad`, `file://path`.
- `--bins`: Number of quantiles (default: 10).
- `--samples-per-bin`: Target (default: 20; warn if <10).
- `--range`: `min_tokens` to `max_tokens` (e.g., 1000:128000).

### 5. Critical Statistical Warning

- **Signal:** The system will output a "Power Warning" if the **Transition Zone** (the bins where the cliff is expected, typically 40-60% of context) has high variance but low sample count (). This is the specific region where "Degradation" must be distinguished from random noise.
