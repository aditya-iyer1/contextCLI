# Pitfalls Research — Signal validation (Alpha)

**Researched:** 2026-03-27  
**Confidence:** MEDIUM–HIGH

## Critical pitfalls

1. **P-hacking / flexible stopping** — Changing bins or thresholds after seeing results invalidates Alpha. **Mitigation:** Pre-register spec (SIG-01) and dataset (SIG-02) before primary runs; document any deviation.

2. **Conflating API noise with length signal** — Small N or single run can show spurious cliffs. **Mitigation:** Bootstrap CIs, repeated runs, resample stability (SIG-04).

3. **Over-interpreting imported KV runs** — Different stack, different semantics. **Mitigation:** SIG-06 labels and caveats; never primary validation.

4. **Scope creep** — Turning Alpha into doc cleanup or UX. **Mitigation:** DOC-01/02/RUN-01 only if blocking interpretation; otherwise defer.

5. **Weak synthetic control** — If the dataset does not induce measurable degradation, the harness should **fail Alpha** honestly—do not “fix” the dataset post hoc to pass.

## Prevention by phase

- **Spec phase:** Freeze definitions and success criteria in writing.
- **Dataset phase:** Independent review that burial/length manipulation is monotonic and testable.
- **Stats phase:** Reproducible seeds and documented resample counts.
