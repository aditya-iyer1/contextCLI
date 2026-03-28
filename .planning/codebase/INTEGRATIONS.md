# Integrations

## OpenAI Chat Completions

- **Where:** `src/contextcliff/models/openai_client.py`
- **Client:** Official `openai` Python SDK (`OpenAI` class)
- **Auth:** `OPENAI_API_KEY` via environment (when using the **`contextcliff`** CLI, optional `.env` is loaded first in `cli/main.py`; default `override=False`)
- **Usage:** `chat.completions.create` with `messages=[{"role": "user", "content": prompt}]`, `temperature=0.0`
- **Retries:** Up to 3 attempts with exponential backoff on failure
- **Cost:** Heuristic pricing table `PRICING` for `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`; `cost_estimate()` used by `Runner.check_cost()` before a run

## Hugging Face Datasets (NarrativeQA)

- **Where:** `src/contextcliff/data/adapters/narrative_qa.py`
- **API:** `datasets.load_dataset("narrativeqa", streaming=True, split="test", ...)`
- **Auth:** Optional `HF_TOKEN` env for gated/private access (set in shell or `.env` via CLI `load_dotenv` as above)
- **Flags:** `trust_remote_code=True` on load

## Tokenization (length estimation)

- **Where:** `NarrativeQAAdapter` in `src/contextcliff/data/adapters/narrative_qa.py`
- **Library:** `tiktoken` (default encoding `o200k_base`, fallback to `cl100k_base` on failure)
- **Purpose:** `context_tokens` per example for NLDA-style binning in `sampler.py`

## External JSON import (IMP-01)

- **Where:** `contextcliff import` → `import_bridge.artifact_v1.parse_artifact_v1` → SQLite writes via `StateManager` (same `predictions` / `runs` store as internal runs).
- **Artifact:** Root JSON object must include **`schema_version`: `1`**; row shape and validation rules live in `artifact_v1.py`.

## Local persistence

- **SQLite:** `src/contextcliff/runner/state.py` — `state.db` stores `runs` / `predictions` (no HTTP; file-based only).
- **`runs`** rows carry **provenance** for internal vs imported experiments: **`run_source`**, **`external_label`**, **`artifact_ref`** (see schema in `state.py`).

## Not integrated (by design in current code)

- No webhooks, OAuth providers, or third-party observability services in-tree
- **Runner** only wires OpenAI for names containing `"gpt"` or `model_name == "mock"` (`src/contextcliff/runner/engine.py`); other providers raise `NotImplementedError`
