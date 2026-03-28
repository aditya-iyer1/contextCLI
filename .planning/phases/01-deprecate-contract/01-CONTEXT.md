# Phase 1: Deprecate docs & API contract — Context

**Gathered:** 2026-03-27  
**Status:** Ready for execution  
**Source:** Roadmap + REQUIREMENTS (DOC-01, DOC-02, RUN-01)

## Phase boundary

Deliver **documentation honesty** and **CLI/runner clarity** before any schema or import work:

- Long-form docs must not describe in-repo SnapKV / PyramidKV / vLLM `--kv_policy` / KVCache-Factory as if shipped.
- One canonical statement: **in-repo = OpenAI API path + `mock`**; compression experiments run **elsewhere** and may be merged via **import** (later phases).
- Source tree and CLI must not advertise KV-budget or local compression controls.

## Implementation decisions

- **Deprecation style:** Prefer explicit **Deprecated** callouts and short replacement pointers over deleting all historical prose, so git history and readers still see what changed—unless a file is mostly misleading, then trim aggressively.
- **Canonical doc:** `docs/architecture.md` (no root `README.md` yet)—add a prominent **Current execution model** section; keep existing tree overview below if still useful.
- **RUN-01:** Confirm via review + `rg`/`grep`; change only user-visible strings, help text, or misleading comments—**no new abstractions**.

## Canonical references

- `.planning/PROJECT.md` — scope and out-of-scope
- `.planning/REQUIREMENTS.md` — DOC-01, DOC-02, RUN-01
- `.planning/codebase/ARCHITECTURE.md`, `STACK.md` — actual current stack
- Target edits: `docs/full_desc.md`, `docs/blueprint.md`, `docs/architecture_preview.md`, `docs/data_layer.md`, `src/contextcliff/cli/main.py`, `src/contextcliff/runner/engine.py` (comments/help only unless bug found)

## Deferred

- SQLite provenance, import CLI, analysis changes — **later phases**.

---

*Phase: 01-deprecate-contract*
