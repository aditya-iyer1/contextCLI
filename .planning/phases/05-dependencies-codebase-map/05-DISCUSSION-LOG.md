# Phase 5: Dependencies & codebase map — Discussion Log

> **Audit trail only.** Decisions live in `05-CONTEXT.md`.

**Date:** 2026-03-28  
**Phase:** 5 — Dependencies & codebase map  
**Mode:** Requirement-driven defaults (no interactive gray-area session)

---

## Session note

Phase 5 scope is **narrow** per **ROADMAP** and **REQUIREMENTS**: **DEP-01** (declare deps, especially **`python-dotenv`**) and **DOC-03** (refresh **`.planning/codebase/*`**). **STACK.md** already flags the dotenv gap.

Grey areas resolved by defaults in **05-CONTEXT.md**:

| Topic | Resolution |
|-------|------------|
| Which deps to add | At minimum **`python-dotenv`**; quick audit of **`src/`** for other runtime gaps |
| How deep DOC-03 goes | Update **STACK**, **ARCHITECTURE**, **INTEGRATIONS**, **STRUCTURE** for Phases 3–4; patch **CONVENTIONS** / **CONCERNS** / **TESTING** only if factually wrong |
| Phase 1 doc requirements | **Explicitly deferred** — not part of Phase 5 |

## Deferred ideas

- Full **`docs/full_desc.md`** deprecation sweep (**DOC-01**) — remains Phase 1 / backlog.
