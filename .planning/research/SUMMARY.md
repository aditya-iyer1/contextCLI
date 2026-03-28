# Project Research Summary

**Project:** ContextCliff  
**Domain:** Long-context eval harness — signal validation milestone  
**Researched:** 2026-03-27  
**Confidence:** HIGH

## Executive Summary

Alpha is a **validation** milestone: prove the existing harness can detect **real**, **stable** degradation on a **controlled** synthetic dataset using **API/mock** execution only, with **statistics** and a **single interpretable report**. Research aligns with standard practice in eval harness work: pre-defined metrics, sufficient resampling, clear cliff rules, and honest failure when signal is absent. No new architecture or CLI; extend analysis and reporting only as needed.

## Key Findings

### Recommended stack

Stay on **Python + SQLite + existing API client**; add minimal statistical dependencies only if justified by `pyproject.toml` policy.

### Expected features

**Must have:** Signal spec (SIG-01), synthetic dataset (SIG-02), API baseline bins (SIG-03), robustness checks (SIG-04), one cliff rule validated (SIG-05), final report (SIG-07), contract preservation (SIG-08). **Optional sanity:** SIG-06 vs imported runs.

### Architecture approach

Extend **profile/analysis** and **data preparation** within current boundaries; do not fork a second pipeline.

### Critical pitfalls

Pre-registration discipline; sufficient N and resampling; no primary reliance on external KV; avoid scope creep into DOC/RUN work unless blocking.

## Implications for Roadmap

Suggested phase order (maps to user’s seven phases, continuing numbering after v1.0 Phase 5):

1. **Signal contract** — SIG-01 first; freeze before heavy runs.  
2. **Controlled dataset** — SIG-02.  
3. **Baseline API validation** — SIG-03.  
4. **Statistical robustness** — SIG-04.  
5. **Transition validation** — SIG-05.  
6. **External consistency** — SIG-06.  
7. **Final report** — SIG-07, SIG-08.

### Research flags

- **Stats implementation:** Confirm dependency policy before adding scipy/numpy features.  
- **API cost/repeat runs:** Budget enough repeats for stability checks.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Brownfield constraints clear |
| Features | HIGH | User spec exhaustive |
| Architecture | HIGH | No greenfield |
| Pitfalls | MEDIUM | Empirical risk in real API variance |

**Overall confidence:** HIGH for roadmap structure; MEDIUM for empirical pass/fail until runs exist.

### Gaps to address during planning

- Exact model ID and token bin layout for SIG-03 (choose during `/gsd-plan-phase`).  
- Canonical cliff rule choice (delta score vs failure jump vs variance spike—pick one in SIG-01/SIG-05).

## Sources

- `.planning/PROJECT.md` — milestone contract  
- Standard eval practice: pre-registration, bootstrap, bin-wise comparison  

---
*Research completed: 2026-03-27*  
*Ready for roadmap: yes*
