"""Helpers for ``profile``: run config, optional manifest join, filters, report sections."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# --- Keys documented for users (see docs/architecture.md) ---

ANALYSIS_FILTERS_KEY = "analysis_filters"
COMPRESSION_METADATA_KEY = "compression_active"
NEEDLE_BUCKET_KEY = "needle_position_bucket"

_WARN_BAD_CONFIG = "runs.config is not valid JSON; analysis_filters ignored."
_WARN_COMPRESSION_NO_MANIFEST = (
    "compression_active_only was requested in analysis_filters but no manifest was "
    "provided; compression filter was not applied."
)


def parse_run_config(config_str: Optional[str]) -> Tuple[Dict[str, Any], List[str]]:
    """Parse ``runs.config`` JSON. Returns ``({}, [warning])`` on missing/invalid input."""
    warnings: List[str] = []
    if config_str is None or (isinstance(config_str, str) and not str(config_str).strip()):
        return {}, warnings
    if not isinstance(config_str, str):
        return {}, warnings
    try:
        data = json.loads(config_str)
    except json.JSONDecodeError:
        warnings.append(_WARN_BAD_CONFIG)
        return {}, warnings
    if not isinstance(data, dict):
        warnings.append(_WARN_BAD_CONFIG)
        return {}, warnings
    return data, warnings


def effective_filters(
    run_config: Dict[str, Any],
    cli_min: Optional[int],
    cli_max: Optional[int],
) -> Dict[str, Any]:
    """Merge ``run_config['analysis_filters']`` with CLI token bounds (CLI wins)."""
    base = run_config.get(ANALYSIS_FILTERS_KEY)
    if not isinstance(base, dict):
        base = {}
    out = dict(base)
    if cli_min is not None:
        out["min_prompt_tokens"] = cli_min
    if cli_max is not None:
        out["max_prompt_tokens"] = cli_max
    return out


def load_manifest_df(path: str) -> pd.DataFrame:
    """Load manifest JSON (array of examples) into a DataFrame with ``id`` and ``metadata``."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        raise ValueError("manifest must be a JSON array")
    rows = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"manifest[{i}] must be an object")
        eid = item.get("id")
        if eid is None:
            raise ValueError(f"manifest[{i}] missing id")
        md = item.get("metadata")
        if md is not None and not isinstance(md, dict):
            md = {}
        rows.append({"id": str(eid), "metadata": md if isinstance(md, dict) else {}})
    return pd.DataFrame(rows)


def _metadata_get(row: Any, key: str) -> Any:
    if row is None or (isinstance(row, float) and pd.isna(row)):
        return None
    if isinstance(row, dict):
        return row.get(key)
    return None


def apply_prediction_filters(
    df: pd.DataFrame,
    filters: Dict[str, Any],
    manifest_df: Optional[pd.DataFrame],
) -> Tuple[pd.DataFrame, List[str]]:
    """Apply token and optional compression filters. Returns filtered frame and warnings."""
    warnings: List[str] = []
    if df.empty:
        return df, warnings

    out = df.copy()
    min_t = filters.get("min_prompt_tokens")
    max_t = filters.get("max_prompt_tokens")
    if min_t is not None:
        out = out[out["prompt_tokens"] >= int(min_t)]
    if max_t is not None:
        out = out[out["prompt_tokens"] <= int(max_t)]

    comp_only = bool(filters.get("compression_active_only", False))
    if not comp_only:
        return out.reset_index(drop=True), warnings

    if manifest_df is None or manifest_df.empty:
        warnings.append(_WARN_COMPRESSION_NO_MANIFEST)
        return out.reset_index(drop=True), warnings

    m = manifest_df[["id", "metadata"]].copy()
    merged = out.merge(m, left_on="example_id", right_on="id", how="left")

    def _is_compression_active(meta: Any) -> bool:
        if meta is None or (isinstance(meta, float) and pd.isna(meta)):
            return False
        if not isinstance(meta, dict):
            return False
        return meta.get(COMPRESSION_METADATA_KEY) is True

    mask = merged["metadata"].apply(_is_compression_active)
    merged = merged[mask].copy()
    merged = merged.drop(columns=["id", "metadata"], errors="ignore")
    # Keep only original prediction columns
    pred_cols = [c for c in df.columns if c in merged.columns]
    return merged[pred_cols].reset_index(drop=True), warnings


def build_positional_section(
    df: pd.DataFrame,
    manifest_df: Optional[pd.DataFrame],
) -> Optional[str]:
    """Markdown section (heading + table) of mean F1 by ``needle_position_bucket``, or ``None``."""
    if df.empty or manifest_df is None or manifest_df.empty:
        return None

    m = manifest_df[["id", "metadata"]].copy()
    merged = df.merge(m, left_on="example_id", right_on="id", how="left")

    def _bucket(meta: Any) -> str:
        b = _metadata_get(meta, NEEDLE_BUCKET_KEY)
        if b is None:
            return ""
        s = str(b).strip()
        return s

    merged["_bucket"] = merged["metadata"].apply(_bucket)
    merged = merged[merged["_bucket"].str.len() > 0]
    if merged.empty:
        return None

    lines: List[str] = [
        "## Positional diagnostics\n\n",
        "| Position bucket | Count | Mean F1 |\n",
        "|---|---|---|\n",
    ]
    for bucket, sub in merged.groupby("_bucket", observed=True):
        n = len(sub)
        mf = float(sub["f1_score"].mean()) if "f1_score" in sub.columns else 0.0
        lines.append(f"| {bucket} | {n} | {mf:.3f} |\n")
    lines.append("\n")
    return "".join(lines)


def build_caveats_section(provenance: Dict[str, Any], run_config: Dict[str, Any]) -> Optional[str]:
    """Return markdown body for ``## Caveats`` or ``None`` if no triggers."""
    bullets: List[str] = []

    rs = provenance.get("run_source")
    if rs == "imported":
        bullets.append(
            "This run was **imported** from an external artifact; metrics reflect that "
            "execution path, not in-repo API timing semantics."
        )
        bullets.append(
            "F1 and EM are comparable **only as scoring metrics**; they do not imply "
            "identical experimental conditions between internal harness runs and imported runs."
        )

    ar = provenance.get("artifact_ref")
    if ar:
        bullets.append(
            f"**Artifact reference:** stored label points to external data (`artifact_ref`); "
            f"interpret scores in that context."
        )

    for key in ("method", "compression_method", "model"):
        if run_config.get(key) is not None:
            bullets.append(f"Run metadata includes **`{key}`**; method assumptions may differ from the default harness.")

    af = run_config.get(ANALYSIS_FILTERS_KEY)
    if isinstance(af, dict) and af:
        bullets.append("**analysis_filters** were applied for this report; subsets may differ from the full run.")

    if not bullets:
        return None

    body = "\n".join(f"- {b}" for b in bullets)
    return body + "\n"


def build_metrics_interpretation_note(
    provenance: Dict[str, Any],
    run_config: Dict[str, Any],
) -> str:
    """Fixed metrics interpretation: latency vs throughput; optional batch metadata."""
    lines: List[str] = []
    lines.append(
        "- **`latency_ms`** in the database is **per-request wall time** (milliseconds), "
        "whether recorded by the in-repo runner or imported from an artifact."
    )
    lines.append(
        "- **Throughput** (examples per second, batch scheduling) is **not** stored per row. "
        "**Do not** treat the mean of `latency_ms` as throughput or batch rate."
    )
    bs = run_config.get("batch_size")
    tw = run_config.get("total_wall_clock_s")
    if isinstance(bs, (int, float)) and isinstance(tw, (int, float)) and tw > 0:
        lines.append(
            f"- Optional external metadata: `batch_size={int(bs)}`, `total_wall_clock_s={float(tw):.3f}`. "
            "You may compute throughput as **N / total_wall_clock_s** only when **N** is the full evaluated "
            "count for that wall-clock interval (not inferred from mean latency alone)."
        )
    if provenance.get("run_source") == "imported":
        lines.append(
            "- Imported runs may omit or differ in timing fields; treat latency as reported by the source artifact."
        )
    return "\n".join(lines) + "\n"
