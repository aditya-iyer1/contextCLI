# Conventions

## Style and typing

- **Type hints** used in public methods (`typing` modules: `List`, `Dict`, `Optional`, `Iterator`, etc.)
- **Dataclasses** for core DTOs: `Example` is `frozen=True`; `Prediction` and `EvalRecord` are mutable (`src/contextcliff/data/formats.py`)
- **Abstract base classes** for extension points: `BaseAdapter`, `ModelClient` (`abc.ABC` + `@abstractmethod`)

## Docstrings

- Module-level comments explain intent (e.g. `cli/main.py`, `formats.py`)
- Classes and non-trivial methods often have short docstrings; not uniformly enforced across every function

## CLI patterns (`src/contextcliff/cli/main.py`)

- **`click`**: Top-level `@click.group()`; subcommands via `@main.command()`
- **Options:** `@click.option` for flags (`--dataset`, `--bins`, `--manifest`, `--model`)
- **Errors:** Broad `try/except` with `click.echo` for user-facing messages on `run` and `profile`

## Logging and user output

- **Runner** uses `print()` for progress (`src/contextcliff/runner/engine.py`)
- **Sampler** uses `print()` for binning diagnostics (`src/contextcliff/data/sampler.py`)
- **`logging`** imported in `engine.py` but not heavily used in the shown paths—stdout is the primary UX

## Prompt construction

- **Runner** builds a fixed template: `Context:\n{example.context}\n\nQuestion:\n{example.question}\nAnswer:` (`src/contextcliff/runner/engine.py`)
- **NarrativeQAAdapter** embeds a system-style prefix in `context` via `SYSTEM_PROMPT` + document + question (`src/contextcliff/data/adapters/narrative_qa.py`)

## Serialization

- **Manifest:** `dataclasses.asdict` + `json.dump` in `sampler.py` → `manifest.json`
- **DB:** SQLite with explicit column lists in `StateManager.save_prediction` (`src/contextcliff/runner/state.py`)

## Error semantics for failed predictions

- On exception, `Runner` stores `parsed_output` with error text and sets `EvalRecord.failure_type` (`engine.py`); DB column `error` stores a derived message when `"Error"` appears in `parsed_output`
