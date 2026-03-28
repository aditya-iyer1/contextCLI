# Architecture Research — Signal validation (Alpha)

**Researched:** 2026-03-27  
**Confidence:** HIGH

## Existing architecture (do not replace)

- **prepare → run → import → profile** pipeline with SQLite as store.
- **Internal vs imported** run provenance (STA-01, IMP-01).
- **Analysis:** `ResultBinner`, `CliffProfiler`, reporting.

## Integration points for Alpha

1. **Signal spec** — Primarily `.planning` + `docs/` prose; formulas mirrored in analysis code comments or a small `signals.py` (only if needed—avoid refactors).
2. **Synthetic data** — New fixture directory or generator consumed by **prepare** path already used for datasets (match existing adapter patterns).
3. **Statistics** — Extend **profile** / internal analysis helpers used by `profile_report` rather than a parallel reporting system.
4. **Cliff rule** — One explicit implementation path in `CliffProfiler` (or adjacent module) with tests on controlled data.

## Data flow (unchanged at boundaries)

Manifest → Runner (API/mock) → SQLite → bin → profile/report.

## Build order

1. Signal definitions (no behavior change until spec is fixed).  
2. Dataset + manifest.  
3. Runs + stored results.  
4. Analysis extensions + report template.
