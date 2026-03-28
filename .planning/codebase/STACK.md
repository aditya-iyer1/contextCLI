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
| Env / optional `.env` | `python-dotenv` (`load_dotenv()` only in `cli/main.py` before other imports; default `override=False` does not replace existing env vars) |
| Viz / reporting | `matplotlib`, `seaborn` |
| Types / config | `pydantic` (listed; usage in codebase may be minimal—verify before relying on it) |
| Terminal | `rich` |

## Environment

- **`.env`** (optional): when using the **`contextcliff`** CLI, `load_dotenv()` in `cli/main.py` loads `OPENAI_API_KEY` and optional `HF_TOKEN` before adapters run. Library-only imports (no CLI) do not auto-load `.env`.

## Configuration files

- **`pyproject.toml`**: Project metadata, dependencies, entry point
- **`.env`**: Expected for `OPENAI_API_KEY` and optional `HF_TOKEN` when running via CLI (`cli/main.py` loads it); set env vars yourself for non-CLI use

## Generated / local artifacts (not source)

- **`manifest.json`**: Produced by `balance_samples` in `src/contextcliff/data/sampler.py` (default path repo root)
- **`state.db`**: SQLite DB for run predictions (`src/contextcliff/runner/state.py`, default `state.db` in cwd)
- **`report_<run_id>.md`**: Written by `contextcliff profile` (`src/contextcliff/cli/main.py`)

## Scripts and one-off tools

- **`dry_run.sh`**: End-to-end dry run using `manifest.json` and `contextcliff run` with `--model mock`
- **`test.py`**, **`verify_sampler.py`**, **`debug_db.py`**: Ad hoc diagnostics at repo root (not a formal test suite)
