"""Tests for SIG-02 alpha_synthetic generator and manifest path."""

import json
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

import pytest

from contextcliff.data.alpha_synthetic_generator import build_alpha_synthetic_examples


def test_manifest_determinism():
    a = build_alpha_synthetic_examples(4, 2, 42)
    b = build_alpha_synthetic_examples(4, 2, 42)
    ja = json.dumps([asdict(x) for x in a], sort_keys=True)
    jb = json.dumps([asdict(x) for x in b], sort_keys=True)
    assert ja == jb


def test_monotonic_min_tokens_per_bin():
    examples = build_alpha_synthetic_examples(5, 3, 0)
    by_bin: dict[int, list[int]] = defaultdict(list)
    for ex in examples:
        by_bin[ex.metadata["alpha_bin"]].append(ex.context_tokens)
    mins = [min(by_bin[i]) for i in range(1, 6)]
    for i in range(len(mins) - 1):
        assert mins[i] < mins[i + 1]


def test_prepare_writes_manifest_with_alpha_bin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    r = subprocess.run(
        [sys.executable, "-m", "contextcliff.cli.main", "prepare", "--dataset", "alpha_synthetic", "--bins", "4"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    mf = tmp_path / "manifest.json"
    assert mf.is_file()
    data = json.loads(mf.read_text())
    assert any("alpha_bin" in json.dumps(row.get("metadata", {})) for row in data)
