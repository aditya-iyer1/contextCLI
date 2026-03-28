# Alpha (v1.1) — Canonical signal specification (SIG-01)

**Status:** LOCKED — Phase 6 definition only. No dataset, code, KV, or external comparisons here.  
**Date:** 2026-03-27  
**Score metric (Alpha):** exact match (EM) on the task, in \([0,1]\) per example.

---

## Locked decisions (immutable for Alpha)

| # | Decision | Choice |
|---|----------|--------|
| L1 | **Degradation** | Soft monotonic trend + **statistical separation** (not pure monotonicity, not a single arbitrary score threshold). |
| L2 | **Transition (cliff)** | **Exactly one** primary rule: **Δ(score)** between **adjacent** length bins. |
| L3 | **CI method** | **Bootstrap only.** One global resample count **\(B\)** for Alpha; **\(B\)** is fixed when first used and **identical** for all bins, Δs, and phases that compute CIs. |

If L1–L3 change after this lock, Alpha results are **not** comparable across artifacts.

---

## 1. Variance (three definitions)

**Bins:** Length bins are ordered \(k=1,\ldots,K\) (short → long). All sums/averages are over examples **within** a bin unless stated.

### 1.1 Across bins — **primary**

- **Within-bin spread:** For bin \(k\), let \(s_{k,j}\) be EM of example \(j\) in that bin, \(j=1,\ldots,n_k\).  
  **\(\mathrm{Var}_{\mathrm{bin}}(k) = \mathrm{Var}_j(s_{k,j})\)** (sample variance; \(n_k<2\) → undefined, report and exclude from variance claims for that bin).

### 1.2 Across runs — **stability**

- **Same bin, repeated runs:** For bin \(k\), let \(\bar{s}_k^{(r)}\) be the **mean EM** in run \(r\), \(r=1,\ldots,R\).  
  **\(\mathrm{Var}_{\mathrm{runs}}(k) = \mathrm{Var}_r(\bar{s}_k^{(r)})\)**.  
  Used to separate **noise** from **reproducible** shifts.

### 1.3 Across methods — **secondary (Phase 11 only)**

- Compares statistics computed **separately** per method (e.g., internal API vs imported external). **Not** part of primary Alpha signal; **sanity / direction only**.

---

## 2. Degradation (canonical)

**Soft monotonic:** Expect \(\mathbb{E}[\bar{s}_k]\) to **not increase** as \(k\) increases (generally downward with length).

**Hard (must meet at least one):**

- **(D1) CI separation:** For **some** adjacent pair \((k,k+1)\), the **two-sided \(100(1-\alpha)\%\) bootstrap CIs** for \(\bar{s}_k\) and \(\bar{s}_{k+1}\) (same \(\alpha\), same \(B\)) **do not overlap**; **or**
- **(D2) Slope:** Weighted least-squares slope of \(\bar{s}_k\) vs \(k\) (bin index) is **negative**, and its **bootstrap CI** excludes 0.

**Rejected for Alpha:** strict monotonicity at every step; a single fixed score cutoff with no CI; any rule that ignores bootstrap CIs for bin means.

**Parameters:** \(\alpha\) fixed for Alpha (e.g. 0.05); document in run metadata. Same \(\alpha\) for all degradation and cliff CIs.

---

## 3. Transition — **cliff** (single primary definition)

**Adjacent-bin delta (only primary rule):**

\[
\Delta_k = \bar{s}_k - \bar{s}_{k+1}, \quad k = 1,\ldots,K-1
\]

(\(\bar{s}_k\) = mean EM in bin \(k\); bins short → long.)

**Cliff at boundary \(k\):** \(\Delta_k\) is a **cliff** iff:

1. **Magnitude / significance:** The **two-sided bootstrap CI for \(\Delta_k\)** (from paired or independent bootstrap of bin means per protocol fixed at implementation—**one** protocol for all \(k\)) **excludes 0** in the direction \(\Delta_k > 0\) (score drops moving to longer context), **and**
2. **Resample stability:** In a **majority** of the \(B\) bootstrap resamples used for that CI construction, the sign of the resampled \(\Delta_k\) **matches** the sign of the point estimate \(\hat{\Delta}_k\) (same direction; no arbitrary “flip”).

**Optional diagnostic only (not definitional):** failure-rate jump between adjacent bins — reportable, **not** used to declare primary cliff.

**Rejected for Alpha primary rule:** “variance explosion” as cliff; cliff defined only by a **dataset-specific** raw threshold with **no** bootstrap CI; any second primary cliff definition.

---

## 4. Metrics (minimal set — no others for Alpha)

| Metric | Definition |
|--------|------------|
| **Score** | EM per example; **\(\bar{s}_k\)** = mean EM in bin \(k\). |
| **Failure rate** | Fraction of examples in bin \(k\) with EM \(=0\) (binary incorrect). |
| **Per-bin variance** | \(\mathrm{Var}_{\mathrm{bin}}(k)\) (§1.1). |
| **Bootstrap CI** | Required for \(\bar{s}_k\), \(\Delta_k\), and any declared degradation/cliff conclusion — **\(B\)** fixed globally. |
| **Δ(score)** | \(\Delta_k\) as in §3. |

---

## 5. Statistical criteria (strict)

- **Per bin:** Bootstrap CI for \(\bar{s}_k\) using **\(B\)** resamples, seed policy fixed and logged.
- **Per \(\Delta_k\):** Bootstrap CI for \(\Delta_k\) using **\(B\)** resamples, **same** \(B\) and family as bin CIs.
- **Cliff:** §3 conditions (CI excludes 0 in degradation direction + majority sign stability within the bootstrap scheme).
- **Degradation:** §2 — downward **trend** (soft) **and** (D1) or (D2).

---

## 6. “Real effect” (all required)

A result is a **real effect** for Alpha only if **all** hold:

1. **Direction:** Degradation is **directionally consistent** (§2 soft monotonic expectation; no systematic upward trend with \(k\)).
2. **Separation:** At least **one** adjacent bin pair shows **CI separation** as in (D1), **or** slope criterion (D2) holds.
3. **Cliff stability:** Every reported **primary** cliff (§3) satisfies the **resample stability** clause.
4. **Reproducibility:** Across **repeated runs** (§1.2), the **same** boundaries show cliffs or the same degradation pattern within **Var\(_{\mathrm{runs}}\)** bounds documented in the report.

If **any** fails → **signal invalid** for Alpha (harness fails milestone success criteria).

---

## 7. Signal vs noise

| Verdict | Conditions |
|---------|------------|
| **Signal** | §6 all satisfied. |
| **Noise** | Fails §6 any item; or cliffs flip boundary or sign under repeated runs; or CIs overlap everywhere and slope CI includes 0. |

---

## 8. Parameters to fix at first execution (not in this doc)

| Symbol | Meaning | Lock |
|--------|---------|------|
| **\(B\)** | Bootstrap resample count | First analysis run; then **constant** for Alpha. |
| **\(\alpha\)** | CI level for §2–§3 | Single value for all CIs. |
| **Bootstrap pairing** | How \(\Delta_k\) is bootstrapped | One algorithm; document once. |

---

*End of canonical spec — ~1 page; no KV; no external comparisons; no alternate definitions.*
