# Generic Model Architecture

## 1. Data Layer: Dataset adapters + cahced token lengths

* **Bin-Aware Sampler:** Performs balanced binning of data, logic to scan a large buffer (e.g., 2000 items), sort by length, and force a uniform distribution across quantiles before the Runner Layer ever sees the data

## 2. Runner Layer: 

* Prompt Builder $\rightarrow$ model client $\righarrow$ output parser
* **SQLite State Manager:** Local database (SQLite) to cache succesful API calls. Without this, a crash at the 90th percentile of run results in wasted funds.
* **Cost Governor**: Architecture should explicitly list a pre-flight check that calculates `sum(tokens) * price` per bin to prevent accidental budget burn on massive outlier documents

## 3. Metric Layer: EM/F1 + Failure Taxonomy
* **Telemetry & Normalized F1**: Normalized Token-F1 (`specifications.md`) to detect shallow adaptation (gradual precision loss). Must also capture telemtry (Time-to-first-token/Latency). A spike in latency is often a "canary" signal for a cliff even if the answer is correct


## 4. Profiler Layer: Binning + Stats + Cliff Detection
* **Variance Trigger**: "Cliff" Heuristic: `Variance > 2 * Baseline Variance`. Prevents the code from relying solely on mean accuracy, which is a flaw in existing benchmarks like RULER.

## 5. Report Layer: Plots + Markdown/JSON Summaries + "Safe Cap" Recommendation
* **Quantile-to-token Mapping**: Layer must include the logic to translate internal **Quantile Bins** back into **Fixed Token Counts** (e.g., Bin 4 represents 22k-28k tokens") for the final user report

## 6. ReCLI Layer: One command to run; one command to profile/report


# Code Scaffolding / Project Structure Scaffold

    contextcliff/
    pyproject.toml
    README.md

        src/
            __init__.py

            cli/
                main.py                 # entrypoint: contextcliff ...
                run_eval.py             # run model on dataset → outputs
                profile.py              # bin + analyze → profile
                report.py               # generate plots + markdown/json

            config/
                schema.py               # pydantic configs (model/dataset/run) (RunConfig, ModelConfig, DatasetConfig, PromptConfig)
                defaults.yaml
                manifest.json           # Run manigest to capture data to make results defensible

            data/
            adapters/
                narrativeqa.py        # dataset loader → Example objects
            formats.py              # Example, Prediction, EvalRecord dataclasses
            tokenization.py         # token counting abstraction

            prompting/
                templates.py            # prompt templates
                render.py               # render(example, template) → prompt string

            models/
                base.py                 # ModelClient interface
                openai_api.py           # concrete client (or others)
                caching.py              # optional response cache

            eval/
                metrics.py              # EM, F1
                normalize.py            # answer normalization
                parse.py                # parse model output → answer string
                failures.py             # failure types & counters

            analysis/
                binning.py              # quantile/fixed bins
                stats.py                # mean/var/bootstrap
                cliff.py                # transition detection rules

            reporting/
                plots.py                # matplotlib only
                render_md.py            # markdown report
                render_json.py          # machine-readable profile

            outputs/
                runs/                     # raw run artifacts
                profiles/                 # computed bin summaries
                reports/                  # md/html + figures


# Minimal Data Contracts

    # data/formats.py
    @dataclass
    class Example:
        id: str
        context: str
        question: str
        answers: list[str]
        context_tokens: int

    @dataclass
    class Prediction:
        id: str
        raw_output: str
        parsed_answer: str | None
        prompt_tokens: int
        completion_tokens: int

    @dataclass
    class EvalRecord:
        id: str
        context_tokens: int
        em: float
        f1: float
        failure_type: str | None

Separation prevents analysis code from knowing anything about OpenAI respones, prompt formats, etc.

# Key Tradeoffs

## 1. Bins: Quantiles vs Fixed Width
* Quantiles: Stable variance estimates; easier stats
* Fixed Width: Interpretable token thresholds; risk sparse tail bins

Compromise: Quantiles for analysis + Convert to token thresholds in the final recommendation

## 2. Metric: EM-only vs EM+F1
* Em is crisp but harsh; F1 gives gradient signal (Especially for QA)
* If you care about "catastrophic failure", track failure-rate alongside

## 3. Cost control vs Statistical Power
* Want enough samples per bin to trust variance
* Long contexts cost money

Optimal Design (Cost-Aware): Start with a pilot run (small n per bin), then allocate more samples only near suspected transition bins

## 4. Cliff Definition
* Can define it via:
    * Variance spike
    * Failure rate spike
    * Sharp mean drop
    * A composite

Start transparent: Two-threshold rule (Variance Spiek + Failure Spike); easier to explain and hard to game


Based on the `architecture.md` file provided in the sources and the "Secret Sauce" requirements derived from your research (specifically the need for "Natural Length" enforcement and "Variance" detection), here is an evaluation of your repository structure.

### **Verdict: Conditional Go**
The high-level layer separation (Data $\rightarrow$ Runner $\rightarrow$ Metric $\rightarrow$ Profiler) is **fundamentally sound**. It correctly decouples "running the test" from "analyzing the result," which is crucial for the "Black-box Determinism" you committed to in `overview.md`.

However, to support the specific **risk mitigations** you agreed to (specifically the **Bin-Aware Sampler** and **SQLite State Manager**), you must ensure your implementation phase creates specific modules rather than monolithic files.

Below is the **Validated Folder Structure** you should implement to ensure the architecture meets the PRD requirements.

---

### **Recommended Implementation Structure**

```text
contextcliff/
├── __init__.py
├── cli.py                    # [ReCLI Layer] Entry point (commands: run, profile)
├── config.py                 # Configuration (API keys, cost limits)
│
├── data/                     # [Data Layer]
│   ├── __init__.py
│   ├── adapters.py           # Loaders for NarrativeQA, SQuAD
│   └── sampler.py            # [CRITICAL] Implements "Bin-Aware Sampling" & "NLDA"
│                             # Logic: Scan 2k samples -> Sort -> Select N per bin [Source 34]
│
├── models/                   # [Runner Layer Part A]
│   ├── __init__.py
│   ├── base.py               # Abstract Base Class (handles retries/backoff)
│   ├── openai.py             # Clients for GPT-4 / DeepSeek
│   └── huggingface.py        # Local clients (if needed)
│
├── runner/                   # [Runner Layer Part B]
│   ├── __init__.py
│   ├── engine.py             # The main evaluation loop
│   ├── governor.py           # [CRITICAL] "Cost Governor" (Pre-flight budget check) [Source 34]
│   └── state.py              # [CRITICAL] SQLite State Manager (Resume capability) [Source 34]
│
├── metrics/                  # [Metric Layer]
│   ├── __init__.py
│   ├── scorers.py            # Normalized Token-F1 implementation [Source 35]
│   └── taxonomy.py           # Failure Mode Classifier (JSON errors, Refusals) [Source 35]
│
├── profiler/                 # [Profiler Layer]
│   ├── __init__.py
│   ├── binning.py            # Logic to slice results into Quantiles vs Fixed-Width [Source 36]
│   └── cliff.py              # [CRITICAL] Variance Trigger Logic (>2x std dev) [Source 35]
│
└── reports/                  # [Report Layer]
    ├── __init__.py
    ├── generator.py          # JSON artifact creator
    └── plots.py              # Visualization (Matplotlib/Seaborn)
```

### **Critical Implementation Checks**

1.  **The `data/sampler.py` Module:**
    *   **Requirement:** Do not put sampling logic in `cli.py`. The "Natural Length" logic (scanning 2,000 items to find the long tail) is complex and needs its own home. This module must strictly enforce that **no truncation** occurs during the loading phase.

2.  **The `runner/state.py` Module:**
    *   **Requirement:** This file must initialize a simple SQLite table (`runs` table with columns: `prompt_hash`, `model`, `output`, `status`). Before `engine.py` calls the API, it *must* check this local DB. This is the only way to satisfy the "Solo-Engineer/Cost-Aware" constraint.

3.  **The `metrics/taxonomy.py` Module:**
    *   **Requirement:** This should not just be a dictionary. It needs a function `classify_failure(prediction)` that returns a string (`"reasoning_error"`, `"context_refusal"`, `"format_error"`). This taxonomy is required to distinguish "Context Rot" (hallucination) from "Capacity Failure" (refusal) in your final report.

4.  **The `profiler/cliff.py` Module:**
    *   **Requirement:** Hardcode the heuristic here: **"Transition = Region where Variance > $2\times$ Baseline Variance."** Separating this logic allows you to tweak the threshold (e.g., to 1.5x) later without breaking the rest of the pipeline.

TO add:

# CACHING - Mandatory

### **Final Instruction**
If this structure makes sense to you, you are ready to begin implementation. Start with **`data/sampler.py`**—if you can't get the distribution right, the rest of the tool doesn't matter.



# Project Implementation Order


The Optimized "ContextCliff" Build Order
This order ensures that the Data Distribution (the most important scientific part) is handled before you spend a single cent on APIs.

Phase 1: The Data Foundation (The "No-Cost" Phase)
Step 0: Skeleton. CLI stubs + pyproject.toml.

Step 1: The Sampler (data/sampler.py + data/formats.py).

Goal: Load NarrativeQA -> Tokenize with tiktoken -> Sort by Length -> Output a Histogram.

Why: You need to see if you even have enough long-context samples before you build the runner.

Step 2: The "Balanced" Manifest.

Create a command: contextcliff prepare --dataset narrativeqa --samples-per-bin 20.

This outputs a manifest.json containing the IDs of the samples you will actually test.

Phase 2: The Execution Engine (The "Cost-Sensitive" Phase)
Step 3: SQLite State Manager (runner/state.py).

Build the cache BEFORE the model client. If you call the API and it's not being logged to SQLite, you are burning money.

Step 4: The Resilient Runner (models/base.py + models/openai.py).

Implement Retry with Backoff for HTTP 500s.

Verify with a "Mock Model" that returns random text first.

Step 5: The "Run" Command.

Execution: contextcliff run --manifest manifest.json.

This populates your predictions.jsonl.

Phase 3: Analysis & The Cliff (The "Science" Phase)
Step 6: Metrics & Taxonomy (metrics/scorers.py).

Implement Normalized Token-F1.

Implement the Failure Classifier (identifying if the model just "gave up").

Step 7: The Cliff Engine (profiler/cliff.py).

This is where you implement the Variance Spike (>2x) and Mean Drop (>30%) logic.

Step 8: The Report. * Generate the "Safe Operating Cap" recommendation.

