"""Versioned import artifact — schema ``1`` only.

Top-level JSON shape::

    {
      "schema_version": "1",
      "run_metadata": { ... },
      "predictions": [
        {
          "example_id": "string",
          "raw_output": "string",
          "prompt_tokens": 0,
          "completion_tokens": 0,
          "latency_ms": 0.0,
          "error": null,
          "f1_score": 0.0,
          "em_score": 0.0
        }
      ]
    }

``run_metadata`` is persisted as JSON in ``runs.config``. Per-example rows map to the
``predictions`` table (no provenance columns on ``predictions``).
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

SUPPORTED_SCHEMA_VERSION = "1"


def _json_int(value: Any, default: int = 0) -> int:
    """JSON ``null`` or absent key → ``default``; otherwise ``int(value)``."""
    if value is None:
        return default
    return int(value)


def _json_float(value: Any, default: float = 0.0) -> float:
    """JSON ``null`` or absent key → ``default``; otherwise ``float(value)``."""
    if value is None:
        return default
    return float(value)


def parse_artifact_v1(raw: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Validate and normalize a v1 artifact. Returns ``(run_metadata, prediction_rows)``."""
    ver = raw.get("schema_version")
    if ver != SUPPORTED_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported schema_version: {ver!r}; only {SUPPORTED_SCHEMA_VERSION!r} is supported."
        )

    meta = raw.get("run_metadata")
    if not isinstance(meta, dict):
        raise ValueError("run_metadata must be a JSON object")

    preds = raw.get("predictions")
    if not isinstance(preds, list) or len(preds) == 0:
        raise ValueError("predictions must be a non-empty array")

    out: List[Dict[str, Any]] = []
    for i, p in enumerate(preds):
        if not isinstance(p, dict):
            raise ValueError(f"predictions[{i}] must be an object")
        ex = p.get("example_id")
        if ex is None or (isinstance(ex, str) and not ex.strip()):
            raise ValueError(f"predictions[{i}].example_id is required")
        if p.get("raw_output") is None:
            raise ValueError(f"predictions[{i}].raw_output is required")

        err = p.get("error")
        if err is not None and not isinstance(err, str):
            err = str(err)

        out.append(
            {
                "example_id": str(ex),
                "raw_output": str(p.get("raw_output")),
                "prompt_tokens": _json_int(p.get("prompt_tokens"), 0),
                "completion_tokens": _json_int(p.get("completion_tokens"), 0),
                "latency_ms": _json_float(p.get("latency_ms"), 0.0),
                "error": err,
                "f1_score": _json_float(p.get("f1_score"), 0.0),
                "em_score": _json_float(p.get("em_score"), 0.0),
            }
        )

    return meta, out
