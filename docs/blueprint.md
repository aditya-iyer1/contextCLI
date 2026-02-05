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
   4. **Making it Usable**:
      - **Visual plot Requirement**:
        - **X-axis:** Natural Context Length (Tokens).
        - **Y-axis:** Performance (Primary) + Variance (Secondary, e.g., error bars).
        - **Markers:** Explicitly label the **"Safe Operating Cap"**—the maximum token count before variance exceeds a predefined "Stability Threshold".
        - **Machine-Readable Export**: A JSON file containing the `[min, median, max]` tokens and `n_samples` for every bin to ensure the results are reproducible.

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
4. **Pytest**: Essential for the "Agentic Workflow". Will want to write a test that checks if the "Output Parser" actually works before I spend any money on long-context calls.]

## Follow-Up Questions

1. **Budget Constraint:** What is your specific "per-model" budget? (e.g., Is <$50 per curve a hard limit?) This determines how aggressively the **Bin-Aware Sampler** needs to work.
2. **Model Selection:** Are you planning to test specific "frontier" models (like GPT-4o) or "open-weights" models (like Qwen2.5) via API providers?
3. **Stability Definition:** What constitutes an "unacceptable" variance spike for your use case? (e.g., A 10% increase in standard deviation or a specific drop in the 10th percentile of scores?)

## CLI User Input:

`contextcliff --data <path_to_data> --model <model_name> --kv_policy <policy> --kv_budget <budget> --task <task_type>`
