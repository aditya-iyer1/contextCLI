# Stack Research — Signal validation (Alpha)

**Researched:** 2026-03-27  
**Confidence:** HIGH (harness already Python/SQLite/API; no new runtime stack)

## Summary

Alpha adds **no new execution stack**: continue **Python 3.x**, **SQLite**, **OpenAI-compatible API** / **mock**, existing **scoring** (`eval/metrics.py`) and **analysis** (`ResultBinner`, `CliffProfiler`). Statistical additions should prefer **stdlib + NumPy/scipy** if already present, or minimal **bootstrap** implementations without new heavy dependencies—verify `pyproject.toml` before adding packages.

## Stack additions for Alpha

| Need | Recommendation | Rationale |
|------|----------------|-----------|
| Bootstrap / CIs | `numpy` + manual bootstrap or `scipy.stats.bootstrap` if scipy available | Standard for resampling; avoid bespoke stats bugs |
| Reporting | Existing `profile_report` / Markdown or HTML path | One report artifact; no new CLI |
| Dataset | JSON or SQLite-seeded examples in-repo | Controlled synthetic cases; same manifest pipeline |

## What not to add

- In-repo KV runtimes, GPU stacks, or new inference engines.
- New CLI frameworks or TUI libraries.

## Integration

Signal definitions live as **documentation + code** in existing analysis modules; thresholds configurable via constants or existing config patterns—**no new CLI flags** per milestone contract.
