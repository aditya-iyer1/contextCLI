# Feature Research — Signal validation (Alpha)

**Domain:** Long-context evaluation harness validation  
**Researched:** 2026-03-27  
**Confidence:** HIGH

## Table stakes (must have for Alpha)

| Feature | Why expected | Complexity |
|---------|----------------|-------------|
| Explicit signal definitions | Without them, “cliff” is meaningless | MEDIUM |
| Controlled synthetic dataset | Ground truth for expected degradation | MEDIUM |
| Per-bin metrics + variance | Detect signal vs noise | MEDIUM |
| Bootstrap / stability checks | Statistical credibility | MEDIUM |
| One cliff rule + repeatability | Interpretable transition detection | MEDIUM |
| Single Alpha report | Pass/fail and human-readable story | LOW |

## Differentiators (nice, not required for pass)

| Feature | Notes |
|---------|--------|
| Multiple cliff rules | Defer; Alpha picks **one** canonical rule (SIG-05) |
| Large model zoo | One API model for baseline is enough (SIG-03) |

## Anti-features

| Feature | Why problematic |
|---------|-----------------|
| Native KV in-repo | Violates Omega contract |
| New CLI commands | Out of scope |
| Using external KV as primary ground truth | SIG-06 is sanity only |

## MVP (v1.1)

Lock spec → dataset → API runs → stats → cliff validation → report → optional import sanity check.
