# Phase 1: Deprecate docs & API contract — Discussion Log

> **Audit trail only.** Decisions are captured in `01-CONTEXT.md`.

**Date:** 2026-03-27  
**Phase:** 01-deprecate-contract  
**Areas discussed:** Deprecation shape, DOC-02 home, CLI surface, Cross-links

---

## Context gate

| Option | Description | Selected |
|--------|-------------|----------|
| Update | Revise context through discussion | ✓ |
| View | Show existing file | |
| Skip | Exit | |

**User's choice:** Update

## Plans gate

| Option | Description | Selected |
|--------|-------------|----------|
| Continue and replan after | Re-run `/gsd-plan-phase 1` to align plans | ✓ |
| Keep plans | Plans unchanged | |

**User's choice:** Replan after (`/gsd-plan-phase 1`)

---

## 1) Deprecation shape

**User's choice:** **HARD CLEANUP**

- Move misleading KV-era docs to `docs/archive/`.
- Remove or rewrite content implying KV runtime ownership in-repo.
- **Not** a soft warnings-only approach.

---

## 2) DOC-02 home

**User's choice:** **Minimal root `README.md`**

- One-paragraph identity.
- Clear API-only contract.
- Pointer to `docs/architecture.md`.
- `docs/architecture.md` remains source of truth.

---

## 3) CLI surface

**User's choice:** **Update both** module docstrings and CLI help (`--help`, epilog).

- Explicitly state: API/mock-only execution; no KV control; external import for compression experiments.

---

## 4) Cross-links

**User's choice:** **No `.planning` references in user-facing docs**

- User-facing docs stay clean; reference `docs/architecture.md` only (no internal planning paths in shipped README/docs).

---

## Claude's Discretion

- Archive filenames; exact rewrite depth for non-archived stubs.
- Epilog formatting.

## Deferred ideas

None raised outside phase scope.
