# Concerns

## Dependency drift

- **`python-dotenv`** is imported in `src/contextcliff/models/openai_client.py` and `src/contextcliff/data/adapters/narrative_qa.py` but is **not** declared in `pyproject.toml`—fresh installs may fail until added or installed manually.
- **`pydantic`** is listed in `pyproject.toml` but appears **unused** in the surveyed modules; either adopt it for config validation or remove to reduce noise.

## Security and secrets

- **API keys** read from environment (`OPENAI_API_KEY`, `HF_TOKEN`)—ensure `.env` is gitignored and never commit real keys.
- **`ResultBinner.load_run_data`** builds SQL with an f-string embedding `run_id` (`src/contextcliff/analysis/binning.py`). Run IDs are CLI-generated today, but this pattern is **SQL-injection-prone** if `run_id` ever becomes user-controlled raw input—prefer parameterized queries.

## Schema and persistence gaps

- **`EvalRecord.failure_type`** is set in `Runner` on errors but **not** persisted as its own column in SQLite (`state.py` stores `f1_score`, `em_score`, token fields, `error` text). Downstream analysis may lose structured failure classification.
- **`runs` table** is created in `StateManager._init_db` but **not** populated in the reviewed `Runner` flow—possible dead schema or incomplete wiring.

## SQL injection / robustness

- Same as above: `query = f"SELECT * FROM predictions WHERE run_id = '{run_id}'"` in `binning.py` should use bound parameters.

## Product / UX

- **Cost confirmation** is printed but not enforced (`Runner.run` prints estimate; comment in `main.py` says “Future: Add cost confirmation”).
- **Profiling** depends on `prompt_tokens` in DB aligning with “length”; binning uses `prompt_tokens` as a proxy for context length—reasonable but worth documenting when comparing to `context_tokens` in manifests.

## Operational

- **`trust_remote_code=True`** on Hugging Face load increases supply-chain surface—acceptable for research tooling but worth pinning dataset revisions if reproducibility matters.
- **Large `manifest.json` / streaming**: interrupted streams are caught in `sampler.py` with a generic message—partial manifests possible without strong validation.

## Technical debt signals

- **Bare `except` in `narrative_qa.py`** (tiktoken encoding fallback) swallows all exceptions—may hide real misconfiguration.
- **Duplicate / legacy code paths** in `sampler.py` (comments reference alternate merge strategies) suggest iterative edits; consider refactoring for maintainability when extending binning.
