# Testing

## Formal test suite

- **`tests/`** package with **`unittest`** modules: `tests/test_import_bridge.py`, `tests/test_profile_report.py`, `tests/test_profile_phase4.py`
- **Discovery:** from repo root, run **`uv run python -m unittest discover -s tests -p 'test_*.py'`** (or **`uv run python -m unittest`** with explicit module paths)

## Ad hoc scripts (repo root)

| File | Purpose |
|------|---------|
| `test.py` | Loads `manifest.json`, prints length stats and metadata key inspection |
| `verify_sampler.py` | Referenced by `dry_run.sh` to produce `manifest.json` if missing (verify locally—path may vary) |
| `debug_db.py` | SQLite inspection helper |

## Mock model path

- **`MockClient`** is defined inside `src/contextcliff/runner/engine.py` (not under `tests/`)
- **`contextcliff run --manifest ... --model mock`** exercises the full loop without API calls
- **`dry_run.sh`** automates: ensure manifest → `contextcliff run` with mock → `contextcliff profile` using parsed run id

## What is not covered automatically

- No CI config observed in the small file listing (e.g. no `.github/workflows` in the glob snapshot)—assume local verification only
- **OpenAI** paths require `OPENAI_API_KEY` and are not mocked in a dedicated test harness
- **Hugging Face** streaming load is slow/heavy; `prepare` / adapter code is typically validated by manual runs

## Suggested direction (for future work)

- Add **`pytest`** as an optional runner, factor `MockClient` to a test module, and add fixtures for tiny JSON manifests
- Add regression tests for `evaluate_example`, `CliffProfiler.detect_cliff`, and `ResultBinner.bin_results` with small DataFrames if not already covered
