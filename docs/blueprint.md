# ContextCliff CLI Blueprint

This blueprint contains my aggregated, full planning for the ContextCliff CLI. This logs the planned project architecture, the moving parts, and the implementation details. Raw architecture diagram will go in `architecture.md`, and `log.md` will contain my general changelog / major operational/decision changes throughout the couse of the project. This file alone is meant to aggregate information from other sources and research from docs to act as a sole, thorough detailed project breakdown. All tradeoffs, modeling decisions, and implementation details are captured here.

Note: Most project files will be referred to using `src/contextcliff/` as the root directory.

## Project Summary

Measuring the effective reasoning limit of an LLM by evaluating naturally long examples across length bins, treating varaince spikes as first-class signals (the "cliff"), not noise.

### Motivations

Lots of long-context evidence is consistent with the hypothesis that "advertised context length is not the same as reliable reasoning length":

- **Position Sensitivity**: Performance often peaks when relevant evidence is near the beginning/end, and drops it when its in the middle (LITM - Lost in the Middle)
- **Benchmarks** showing "real context size" can be much smaller than claimed when tasks go beyond trivial recall.
- **Broad benchmark** work indicates models still struggle as length increases, and that retrieval/compression only partially closes the gap.

### Primary Method Commitments/Guardrails

#### Natural Length Distribution (NLDA)

- No truncation, padding, synthetic needle inserts
- Each sample is evaluateed at native length
- Group samples into 10 decile bins (quantiles or fixed-width range tokens)
- Report mean + variance + instability per bin

#### Black-box, Deterministic Evaluation

- No activations, no fine-tuning, no LLM-as-judge (unless later justified)
- Prefer **Exact Match / Token-F1 / Execution success** (depending on task)
- Fix randomness: temperature 0; consistent formatting, robust parsing

#### Variance as a Signal (Not Noise)

- Treat a "transition region" as increased variance / bimodaility / failure volatility
- The "safe context cap" is a conservative cutoff before volatility explodes

## High-Level Overview:

0. **Defining the Objective**:
   - **Goal**: "Effective reasoning limit" for a specific task type (e.g., long-doc QA)
   - **Task Family**: QA (NarrativeQA), multi-doc QA, summarization, coreference, etc.
   - **Model access mode**: API vs local; single model vs comparing multiple
1. **Data Layer**: Responsible for data ingestion and formatting with Natural Length Distribution (NLDA)
   - **Goal**: Get a dataset where length varies widely _without manufacturing it_
   - **Ingestion**: You feed the raw filed (PDF/MD) or Narrative QA into the tool.
   - **Normalization**: The tool outputs a `data.json`. This is a "long list" where the every item looks identical (Context, Question, Answer, Source, etc).
   - **Stratification**: `sampler.py` reads `data.json`, tokenizes them, sorts them into 10 decile bins, and picks N sampler per bin.
   - **Output**: `manifest.json`. Once this exists, we can delete the source data and the tool should still work.
2. **Runner Layer**: Responsible for running and formatting the model input and output.
   - **Pre-Flight**: The cost governor reads `manifest.json`, estimates the cost, and asks for confirmation, and asks for user/my confirmation.
   - **The Loop**: For every entry in the manifest:
     - **Prompt Builder** wraps the context/question in a template
     - **Model Client** (OpenAI or Local vLLM) send the request
     - **Output Parser** Cleans the response
   - **Storage**: The Stage Manager saves the results to `state.db`.
     - **Note**: We will likely run this loop ~3 times to get a good variance signal.
3. **Analysis**: Metric & Profiler Layers
   - **Scoring**: Metric Layer reads `state.db`, compares the model's answers to the 'ground truth' using Token-F1, and marks it (0.0 to 1.0).
   - **Profiling**: The Profiler looks at the bins. It calculates the Average Score and the Standard Deviation (Variance) for each bin.
   - **Cliff Detection**: It looks for the 'double spike' — where the score drops and the variance jumps.
   - **Translation**: Ex: It looks at bin 7 (70K-80k tokens) and says: "The Cliff is at 72,000 tokens".
4. **Presentation**: The CLI Layer
   - **Reporting**: Formats a table or a graph (PNG) showing the "safety zone" vs the cliff

## Detailed Overview:

### Data Layer

The data layer contains the logic to ingest the data, normalize it, and stratify it into bins. It takes in `data.json` and outputs `manifest.json`. It contains:

1. **Bin-Aware Sampler**: Performs balanced binning of data, logic to scan a large buffer (e.g., 2000 items), sort by length, and force a uniform distribution across quantiles before the Runner Layer ever sees the data.
   - **Key Tradeoffs**:
     1. Quantiles (Stable Variance Estimates) vs Fixed Width (Interpretable Token Thresholds). We will use quantiles for analysis and convert to token thresholds for the final report.
        - **Quantiles**:
          - More stable sample counts per bin
          - Track each bin's [min_tokens, median_tokens, max_tokens, n]
        - **Fixed Width**:
          - Easier to interpret in tokens but can be sparse in the tail
          - Fixed by token width (e.g., 0-8k, 8-16k,...)
     2. **Cost Control vs. Statistical Power**:
        - Want enough samples per bun to trust variance
        - Long contexts cost money
        - Optimal Design (Cost-Aware): Start with a pilot run (small n per bin), then allocate more samples only near suspected transition bins
   - **What I store per example**:
     - `id`
     - `context`
     - `question`
     - `answer`
     - `length_tokens_context`
     - optional: metadata like domain/topic/source/length
   - **Decision Points**:
     1. Filtering: removing extremely short contexts (no long-context signal)
     2. Handling multiple references / acceptable answers
     3. Cost-aware sampling (Likely not able to run full dataset)
2. **Prompt Template Principles**:
   - Minimal instructions; stable format; deterministic output
   - For F1: Tokenize consistently (SQuAD-style tokenization)
3. **Guardrails**:
   - Don't interpret results as a model ranking - it's a task condition reliability
   - Avoid adding "helpful" scaffolding that changes with context length.
   - Keep output format stable across all bins
   - Ensure each bin has enough samples for variance estimates (even if rough)
   - If tails are sparse, merge top bins rather than hallucination conclusions
4. **Risks**:
   - Primary risk in this later is _data scarcity_ in long-context bins. Since I am not truncating or padding, I am at the mercy of the dataset's inherent distribution.
     - **Refinement**: Implement a distribution auditor. Before running inference, this module should scan my dataset (e.g., narrativeQA) and generate a histogram of token counts.
     - **Replacement Suggestion**: Instead of just dataset adapters, use a bin-aware sampler. If a specific bin (50k-60k tokens) has only 2 samples, the tool should flag this as statistically insignificant or automatically merge it with an adjacent bin to maintain signal integrity. We set this threshold manually, and reject bins with `n < [Threshold]`

### Runner Layer

The runner layer contains the logic to run the mode and save the results to a SQLite database. It takes in `manifest.json` and outputs `state.db`. Here, we want to run a deterministic experiment on each sample, and capture outputs + telemetry. It contains:

1. **Prompt Builder**:
   - **Prompt Sanitization**: Ensure the "Natural length" remains by using a minimal, stable scaffold that does not add significant token overgead or change across bins.
2. **Model Client**:
3. **Output Parser**:
4. **SQLite State Manager**: This is a local database (SQLite) to cache succesful API calls, part of the cost governor. If the CLI crashes, it should resue from the last succesful token bin without re-processing. Without this, a crash at the 90th percentile of run results in wasted funds.
5. **Cost Governor**: This contains the pre-flight check that calculates the estimateed cost of a run (`sum(tokens) * price`) based on the total tokens in the selected bins before sending API requests to prevent accidental budget burn on massive outlier documents.
6. **Guardrails**:
   - "Invalid output" is a failure mode—track it as such.
     Keep retries off by default, if you do retries, log them
7. **Modeling Decisions**:
   - **Record Everything**:
     - raw prompt
     - raw model output
     - parsed answer
     - EM / F1
     - token usage (prompt + completion)
     - runtime
     - any parse failures
8. **Risks**:
   - Key issue is "solo engineer" and "cost aware" constraints. This layer must be highly resilient to network failures and API costs.
   - Fix: Cost governor, SQLite State Manager

### Metric & Analysis Layer

The analysis layer contains the logic to write the metrics, analyze the input, and determine the actual performance over time, and the cliffs. It takes in `state.db` and outputs `metrics.json` and `cliffs.json`. It contains:

1. **Metric Layer**: EM/F1 + Failure Taxonomy
   1. **Telemetry & Normalized F1**: Normalized Token-F1 to detect shallow adaptation (gradual precision loss). Must also capture telemtry (Time-to-first-token/Latency). A spike in latency is often a "canary" signal for a cliff even if the answer is correct.
      - **Key Tradeoff**:
        1. EM is crisp but harsh; F1 gives gradient signal (Especially for QA)
        2. If we care about catastrophic failure, we must track failure-rate alongside
        3. **Metric Choice**: EM/F1, ROUGE (iffy), exact structured output match, etc.
2. **Profiler Layer**: Binning + Stats + Cliff Detection
   1. **Variance Trigger**: "Cliff" Heuristic: `Variance > 2 * Baseline Variance`. Prevents the code from relying solely on mean accuracy, which is a flaw in existing benchmarks like RULER. Cliff detection should factor in mean + variance + instability.
      - **Key Tradeoff**:
        1. **Cliff Definition**:
           - Can define it via:
             - Variance Threshold
             - Failure rate spike
             - Sharp mean drop
             - A composite score
           - **Solution**: Start transparent: Two-threshold rule (Variance spike + Failure Spike); easier to explain and hard to game.
           - **Solution**: The "cliff" should not be defined by a mean score alone. Use _variance spikes_ as the primary signal. If the standard deviation of performance in Bin B is >2x the SD in bin A (the baseline), you have entered the _transition zone_.
             - **Support**: Research suggests "Intelligence Degradation" is often catastrophic (dropping >30%) rather than linear. The profiler should look for this specific non-linear drop-off point.
   2. **Per-Bin, Compute**:
      - Mean score
      - std_score / var_score
      - failure_rate (EM==0 or parse fail)
      - instability: e.g.,
      - bootstrap CI width for mean
      - rolling variance
      - mixture/bimodality indicators (optional, later)
   3. **Cliff Heuristics (V1)**:
      - Transition starts when variance or failure-rate rises sharply relative to previous bins.
      - Degraded region when mean collapses and failure-rate stays high.
      - Safe context cap = the highest bin edge before transition (conservative)
3. **Failure Mode Classifier**: Moving beyond simple EM/F1:
   - Instead of just recording a "0" for a wrong answer, we categorize the failures:
     - **Format Failure**: Model failed to follow the output schema (a common sign of context pressure)
     - **Hallucination**: Model provided an answer not present in the text
     - **Incompleteness**: Model stopped mid-sentence (often due to context window limits)
     - **Justification**: High variance in the "Transition region" is often caused by a mix of correct answers and "format failure"
4. **Guardrails**:
   - Don’t overfit “cliff thresholds.” Start with transparent heuristics + sensitivity checks.
   - Always show uncertainty (CI bands, bootstrap).

### Presentation Layer

The presentation layer contains the logic to write out the metrics, cliffs, and the final report. It also writes out any visualizations/reporting we need for the proejct. It takes in `metrics.json` and `cliffs.json` and outputs `report.md` and `report.png`, as well as the CLI output. It contains:

1. **Report Layer**: Plots + Markdown/JSON Summaries + "Safe Cap" Recommendation
   1. **Quantile-to-token Mapping**: Layer must include the logic to translate internal **Quantile Bins** back into **Fixed Token Counts** (e.g., Bin 4 represents 22k-28k tokens") for the final user report
   2. **ReCLI Layer**: One command to run; one command to profile/report
   3. **Key Deliverable**:
      - A machine-readable + human-readable report:
        - **Stable region**: bins where mean stable + variance low
        - Transition: high variance / volatile outcomes
        - Degraded: persistently low mean + high failure
        - Recommended safe cap: token threshold
   - Current benchmarks give a single score (e.g., "78% accuracy"). Your tool gives an operational constraint (e.g., "Do not exceed 51k tokens for Qwen2.5-7B"). This directly translates to production stability.
   4. **Making it Usable**:
      - **Visual plot Requirement**:
        - **X-axis:** Natural Context Length (Tokens).
        - **Y-axis:** Performance (Primary) + Variance (Secondary, e.g., error bars).
        - **Markers:** Explicitly label the **"Safe Operating Cap"**—the maximum token count before variance exceeds a predefined "Stability Threshold".
        - **Machine-Readable Export**: A JSON file containing the `[min, median, max]` tokens and `n_samples` for every bin to ensure the results are reproducible.

## Major Specifcations

1. **Quantile Binning -> Fixed-Width:** Use quantiles for analysis, convert to token thresholds in the final recommendation.
   - To detect "Variance Spike", need a stable $n$ per bin.
   - "Shallow Long-Context Adaptation" uses percentage based bins to identify transition region
   - Engineers need an operational constraint, rather than statistical abstraction
   - Binning implemented in the `parser`, conversion back to tokens implemented in before the final reporting stage
2. **Network Retry vs Generation Fail**: Handle Transport errors via Backoff, treat empty/malformed/refusal outputs as terminal failures
   - **Rationale**: Transport errors (500s/timeouts) are noise; generation errors (broken JSON/refusals) are the **signal**. Retrying "I cannot help with that" hides the cliff-edge instability we aim to measure
   - **Supporting Info**: Long-context calls (100k+) are high-latency/high-cost; crashing on a timeout is a resource waste. "Context Rot" logic dictates model refusal is a valid data point for the "Degraded Region".
   - **Implementation**:
     - **Transport**: `models/base.py` implements a decorator for HTTP 500/429/RequestTimeout
     - **Logic**: `models/openai.py` (or vLLM) returns a `null` or `Failure` object on parse errors.
     - **Persistence**: `runner/state.py` (SQLite) stores `prompt_hash` + `model_output` immediately after succesful transport to prevent redundant spending.
3. **SQuAD-style Normalized Token-F1**: Use bag-of-words overlap (P/R) for generative QA tasks.
   - **Rationale**: Exact-Match (EM) is too brittle for narrativeQA; it provides binary signal that masks the "gradient of degradation". F1 captures the model's gradual loss of coherence.
   - **Supporting Info**: "Shallow Adaptation" paper uses F1 as the primary "Intelligence" metric $I(L)$. Requires standard normalization (lowercase, strip punctuation/articles).
   - **Implementation**: `metrics/scorers.py`
     - **Logic**: `compute_f1(prediction, ground_truth)` function
     - **Preprocessing**: Integrated into the `Parser` before the scorer is called.
4. **Stratified Stratification by Token Count**: Proactively fill length bins to ensure equal power across context range
   - **Rationale**: Natural-Distributions are usually bottom-heavy. Without stratification, the "cliff" regions will have sparse data, making variance spikes indistinguishable from outlier noise.
   - **Supporting Info**: Wang et al (2026) emphasizes that threshold precision depends on sample density in the 40-50% context range. This turns the pipeline from a "stream" into a "targeted pull".
   - **Implementation**: `data/sampler.py`
     - **Logic**:
       - Scan entire dataset to create a `length_map` (Id -> TokenCount).
       - Define $B$ bins (deciles)
       - For each bin, sample $N$ IDs.
       - If a bin is "starved" (fewer than N available), the CLI must flag a **distribution warning** and pull available samples for that tail
     - **CLI Command**: `contextcliff prepare --dataset narrativeqa --samples-per-bin 20` creates the manifest.json.
5. **Latency Telemetry as a Reasoning Canary**: Capture TFFT and total request duration for every sample to detect "Internal Processing Stress" before accuracy collapses.
   - **Rationale**: High-variance latency is often a leading indicator of a cliff. A model might maintain F1 scores but show "stalling" behavior (massive latency spikes) as it nears its reasoning limit, signaling that the "Stable Region" is ending.
   - **Supporting Info**: "Context Rot" research suggests that as input density inreases, KV-cache management or attention overhead can cause non-linear latency growth. Capturing this allows the Profiler to identify a "Resource Cliff" even if an "Accuracy Cliff" isn't yet visible.
   - **Implementation**: Add `tfft_ms` and `total_duration_ms` to the `Prediction` object/`EvalRecord` in `data/formats.py`
     - **Runner**: `models/base.py` uses `time.perf_counter()` to wrap the inference call
     - **Storage**: Update the SQLite schema in `runner/state.py` to include these telemtry columns.
     - **Profiler**: `profiler/cliff.py` should calculate "Latency Variance" as a secondary signal for the Transition Zone.
6. **Automated Failure Taxonomy**: Programmatically categorize non-correct responses into three distinct error buckets to isolate why the cliff occurs.
   - **Rationale**: A drop in F1 is a "what", a taxonomy is the "why". Distinguishing between a model that forgets the task (Drift) vs. one that gives up (refusal) vs. one that breaks the pipe (Schema) is essential for the failure profile
   - **Supporting Info**: Research on LITM shows that models often drift towards summarizing the end of the context instead of answering query. Identifying false negatie (Refusal when info present) specifially maps to the "Shallow Adaptation" cliff where capacity is exceeded.
   - **Implementation**: `metrics/taxonomy.py`
     - **Logic**:
       - Schema Violation: Triggered if `json.loads()` fails or specific keys are missing
       - Refusal: Regex-based checks for "I am sorry", "not mentioned", "cannot find", etc.
       - Instruction Drift: Heuristic Check - if the answer length exceeds a certain ratio of the ground truth or fails to contain any nouns from the query, it is staged as drift.
     - **Data Layer**: `EvalRecord` must have a `failure_tag` (Enum)
7. **MVE Cliff Detection & Model Comparison**: Use a 5-bin stratified test (4k vs 128k) to compare "Small" vs "Large" model stability curves.
   - **Rationale**: Comparing models with different parameter counts/budgets validations if the "Cliff" is a function of model capacity. The 5-bin approach minimizes API costs while maintaining enough resolution to identify the transition zone.
   - **Supporting Info**: Research on Shallow Long-Context Adaptaion suggests cliff points are task and scale dependent. Using a baseline (0-8k) performance level is needed to calculate "mean drop" and "var spike" relative to optimal behavior.
   - **Implementation**:
     - **Layer**: Profiler/Analysis
     - **Role**: Post-processing engine that compares bin-wise statistics
     - **Logic**:
       - Establish baseline $\mu$ and $\sigma$ from the 4k bin.
       - Flag "Transition" if $\sigma_{bin} \ge 2\sigma_{baseline}$.
       - Flag "Cliff" if $\mu_{bin}$ drops > 30% from $\mu_{baseline}$
   - **Visualization**: Generates a dual-line plot (F1 vs Length) for the two models to visually show the "Shifted Cliff"
8. **Conservative Safe Cap Calculation**: Map quantile failure bins to their token lower bounds for reporting
   - **Rationale**: Statistical Significance requires stable $n$ (quantiles), but engineering requires a concrete token limit. Reporting the lower bound of the first failing bin provides a "safety-first" conservative estimate for production deployments.
   - **Supporting Info**: "Shallow Adaptation" (Wang et al., 2026) suggests that cliff behavior is often sudden; using the lower bound ensures the user stays safely within the "Stable Region" before the transition volatility begins.
   - **Implementation**:
     - **Layer**: Profiler / Report Layer
     - **Role**: Translate statistical analysis into operational constraints
     - **Logic**:
       - Identify `bin_i` where $\sigma$ exceeds threshold or $\mu$ drops > 30%.
       - Query the `Data Layer` for the `min_tokens` value associated with `bin_i`
       - Output this integer as the `Effective Reasoning Limit`.
       - Store the `(Bin_ID, Token_Range)` map in the final report JSON to allow for manual data auditing.

## General Critiques

1. **Pros**:
   - Current benchmarks give a single score (e.g., "78% accuracy"). Your tool gives an operational constraint (e.g., "Do not exceed 51k tokens for Qwen2.5-7B"). This directly translates to production stability.
   - Your focus on "cliff thresholds" and "transition variance" aligns perfectly with cutting-edge findings that degradation is catastrophic (cliff-like) rather than linear. The drop often happens over a narrow 10% range of the context window.
   - Most existing tools use truncation or padding (artificial length). If your CLI enforces "Natural Length Distribution Analysis" (evaluating samples at their original lengths), you solve a major methodological flaw in current evals where truncation confounds results with information loss
   - Stick with the "Natural Length" knob. It is the most scientifically rigorous contribution that can be made, distinguishing the tool from every other NIAH script.
2. **Risks**:
   - **Data Scarcity**: To plot a smooth curve using "natural length" (without truncation), you need a dataset with a perfect distribution of lengths from 1k to 128k tokens. Most datasets are clustered (e.g., SQuAD is <1k tokens). You will need a "Mixed Dataset" strategy (e.g., combining SQuAD for short and NarrativeQA for long) to cover the 5%–95% context range.
   - **Compute Cost**: Generating a curve requires running the model at 10%, 20%, ... 100% context. For a 128k model, this is computationally expensive. Your "One-liner" needs to clarify if this is a one-time profiling run or a CI/CD check.
   - **Multi-Hop Complexity**: The "distance" knob is harder than it looks. It’s not just about absolute position; performance degrades based on the relative distance between two necessary pieces of evidence. Your harness needs to track inter-evidence distance, not just "needle" depth.
3. **Key Implementations**:
   - **Make the Cliff Predictable (40-50% Rule)**:
     - Models often maintain stable performance up to a "critical threshold" (often 40-50% of the max context) before suffering a catastrophic drop (e.g., F1 score dropping form ~0.56 to ~0.30).
     - Don't just look for the drop. Look for transition variance. Just before the cliff, model performance becomes highly unstable (high standard deviation). A spike in variance is the "early warning system" for the risk report.
   - **Natural Length Implementation**:
     - Do not truncate documents to fit a length bucket. Instead, bin test samples by inherent token count.
     - Truncation creates "artifacts" - it might cut off reasoning chains. Padding distorts attention patterns. The CLI should reject datasets that don't naturally span the target context length.
   - **Shallow Adaptation Theory**:
     - Models suffer form "shallow long-context adaptation". They optimize for short/medium contexts during training. When pushed past the threshold, attention weights become too uniformly distributed (high entropy), preventing focus.
     - The risk report should calculate attention entropy. If entropy crosses a certain threshold, the model is entering the "Degraded Region".
4. **Gap Analysis: Has it been done?**
   - Partially, but poorly. Tools like RULER or NIAH exist. However:
     - NIAH is a retrieval proxy, not a reasoning test. Models can pass NIAH while failing actual tasks.
     - Most benchmarks use truncation to fit context windows, which corrups the causal link between length and performance.
     - There is no widely available tool that outputs a "Safe Operating Region" (e.g., "Safe up to 43% context").
   - Does it fill a genuine issue?
     - Yes. There is currently a "blind reliance" on claimed context windows (e.g. "It fits in 128k, so it works").
     - The Gap: Engineers need to know the "Effective Reasoning Length", which is often significantly shorter than the techical context limit. The tool provides this specific number.
5. **Cost & Feasability**:
   - **Hardware Reality**: You cannot run long-context evaluations locally on an M2 with 8GB RAM. A 7B model (like Qwen2.5-7B) requires ~14GB+ of VRAM to process 128k context even with quantization, and the Key-Value (KV) cache for long sequences grows massive, quickly causing Out-Of-Memory errors.
     - **The Fix**: API is cheap. You should use APIs. The cost is surprisingly low if you choose the right models.
       - DeepSeek-V3 is priced at ~$0.27 per 1M input tokens.
       - The Math: To plot one "cliff curve" (testing 10 points from 10k to 100k context), you process roughly 550k tokens.
       - Total Cost: That is roughly 0.15 per curve — you can run hundreds of experiments for <$50
   - This is very realistic for one person. The "heavy lifting" is done by the API provider; the CLI just manages the logic and plotting.
6. **Automation & Testing**:
   - You do not manually test. You use proxy tasks where the "correct answer" is already known (Ground Truth).
   - How to automate:
     - Synthetic Retrieval: Inject a random UUID (e.g., "Passkey: 98123") into a long document. Check if the model outputs "98123". This is a binary (1/0) check you can code in Python
     - Reading Comprehension: Use datasets like NarrativeQA or SQuAD. You feed the model the story + question. You compare the model's text output to the reference answer using F1 Score (word overlap) or Exact Match. No humans required.
   - Is all context different? (The 50K simple vs 50K Complex question)
     - Yes, absolutely. The sources confirm that "Intelligence Degradation" depends on information density and reasoning complexity, not just token count
     - The Evidence: A model might handle 100k tokens of "simple retrieval" (finding a needle) perfectly but suffer a "cliff-like" collapse at 40-50% capacity when doing "multi-hop reasoning" (connecting two distant facts).
     - Your Solution: Your CLI should categorize tests by complexity.
       - Level 1: "Needle in a Haystack" (Simple Retrieval).
       - Level 2: "Multi-hop QA" (Reasoning over density).
       - Result: Your report will likely show the "Simple" cliff at 120k tokens and the "Complex" cliff at 50k tokens.

## Project Architecture (Conceptual — Updated as files are added) -> Check architecture_preview.md for more conceptual breakdown

    contextCLI/
        pyproject.toml                      # dependency management
        README.md                           # project documentation for github

        docs/
            blueprint.md                    # this file, project overview
            architecture.md                 # project architecture
            cli.md                          # cli usage
            log.md                          # logging strategy, major decisions

        src/                                # contains source code for repo

            cli/
                main.py                     # main entrypoint for CLI, contains subcommands
                run_eval.py                 # TBD
                profile.py                  # TBD
                report.py                   # TBD

            config/                         # TBD
                schema.py                   # TBD
                defaults.yaml               # TBD
                manifest.json               # TBD

            data/
                adapters/
                    narrativeqa.py          # dataset loader → Example objects
                adapter.py                  # TBD
                formats.py                  # Contains boilerplate for data structures used by data ingestion pipeline
                sampler.py                  # Ingests, parses, tokenizes, chunks, and stratifies the data - writes to manifest.json

            prompting/                      # TBD
                templates.py                # TBD
                render.py                   # TBD

            models/                         # TBD
                base.py                     # TBD
                openai_api.py               # TBD
                caching.py                  # TBD

            eval/                           # TBD
                metrics.py                  # TBD
                normalize.py                # TBD
                parse.py                    # TBD
                failures.py                 # TBD

            analysis/                       # TBD
                binning.py                  # TBD
                stats.py                    # TBD
                cliff.py                    # TBD

            reporting/                      # TBD
                plots.py                    # TBD
                render_md.py                # TBD
                render_json.py              # TBD

            outputs/
                runs/                       # TBD
                profiles/                   # TBD
                reports/                    # TBD

## Minimal Data Contracts

Data formats implemented in `data/formats.py`.

```python
class Example:
id: str
context: str
question: str
answers: List[str]
context_tokens: int
metadata: Dict[str, Any] = field(default_factory=dict)

class Prediction:
example_id: str
raw_output: str
parsed_output: Optional[str] = None
latency_ms: float = 0.0
tfft_ms: float = 0.0 # Time to first token
usage: Dict[str, int] = field(default_factory=dict) # prompt/completion tokens

class EvalRecord:
example_id: str
context_tokens: int
f1_score: float
em_score: float
failure_type: Optional[str] = None # e.g. "format_error", "refusal", "hallucination"
```

Separation prevents analysis code from knowing anything about OpenAI responses, prompt formats, etc. This makes the code more modular and easier to test.

## Integrating the KV Cache

1. **Engine Toggle**: In phase 2 (Runner) we add a `localengine` that uses vLLM/SGLang
2. **Compression Variable**: We add a `--kv_policy [H20/SnapKV]` and `--kv_budget [0.1 - 1.0]`
3. **The Loop Hole (Plugged) / Compressed KV Logic**: KV Compression doesn't compress the dataset. It compresses the memory.
   - **Workflow**: We run the pipeline once with `--kv_policy none` (baseline). Then we run it again with `--kv_policy snapkv --kv_budget 0.2`
   - **Comparison**: Profiler compares the two `state.db` entries to show how much the cliff moved.

## External Tools

1. **Docker**: Highly recommended for the KV Cache/vLLM part. vLLM has many dependencies (CUDA, specific python versions). Running it in a Docker container on the cloud GPU will save days of environment issues.
2. **SkyPilot or Lambda Labs CLI**: Since I don't have a local GPU, I'll need a way to launch a cloud instance (A100/A6000).
3. **Weights & Biases (Optional)**: If I want "Pro" research charts for the professor, this tool tracks experiments automatically.
4. **Pytest**: Essential for the "Agentic Workflow". Will want to write a test that checks if the "Output Parser" actually works before I spend any money on long-context calls.

## CLI User Input:

`contextcliff --data <path_to_data> --model <model_name> --kv_policy <policy> --kv_budget <budget> --task <task_type>`

Example Output 1:

    $ contextcliff profile --model Qwen2.5-7B --task multi_hop_qa

    FAILURE RISK REPORT
    -------------------
    Max Technical Context: 128,000 tokens
    Critical Threshold:    55,296 tokens (43.2% of max) [HIGH CONFIDENCE]

    ZONES:
    [OK] Stable Region:      0 - 51,200 tokens (Mean F1: 0.56)
    [!!] Transition Zone:    51,200 - 64,000 tokens (High Variance detected)
    [XX] Degraded Region:    > 64,000 tokens (Performance drop: -45.5%)

    RECOMMENDATION:
    Hard cap inference context at 51,000 tokens.
    RoPE extrapolation failure predicted at ~49% context.
