# Stack

## Languages and runtime

- **Python** `>= 3.8` (see `pyproject.toml`)
- Package layout: `src/contextcliff/` with console entry `contextcliff = contextcliff.cli.main:main`

## Build and packaging

- **`uv`** as the build frontend: `[build-system]` uses `uv_build` (`pyproject.toml`)
- Workspace package: `[tool.uv] package = true`

## Core dependencies (runtime)

Declared in `pyproject.toml` `[project].dependencies`:

| Area | Packages |
|------|----------|
| CLI | `click` |
| Data | `datasets` (HuggingFace), `numpy`, `pandas` |
| Tokenization | `tiktoken` |
| LLM API | `openai` |
| Viz / reporting | `matplotlib`, `seaborn` |
| Types / config | `pydantic` (listed; usage in codebase may be minimal—verify before relying on it) |
| Terminal | `rich` |

## Implicit / environment dependencies

- **`python-dotenv`**: Imported in `src/contextcliff/models/openai_client.py` and `src/contextcliff/data/adapters/narrative_qa.py` (`load_dotenv`) but **not** listed in `pyproject.toml`—install separately or add to dependencies for reproducible installs.

## Configuration files

- **`pyproject.toml`**: Project metadata, dependencies, entry point
- **`.env`**: Expected for `OPENAI_API_KEY` (`openai_client.py`) and optional `HF_TOKEN` (`narrative_qa.py`)

## Generated / local artifacts (not source)

- **`manifest.json`**: Produced by `balance_samples` in `src/contextcliff/data/sampler.py` (default path repo root)
- **`state.db`**: SQLite DB for run predictions (`src/contextcliff/runner/state.py`, default `state.db` in cwd)
- **`report_<run_id>.md`**: Written by `contextcliff profile` (`src/contextcliff/cli/main.py`)

## Scripts and one-off tools

- **`dry_run.sh`**: End-to-end dry run using `manifest.json` and `contextcliff run` with `--model mock`
- **`test.py`**, **`verify_sampler.py`**, **`debug_db.py`**: Ad hoc diagnostics at repo root (not a formal test suite)
