"""Tests for import bridge and collision rules (IMP-01)."""

import json
import os
import tempfile
import unittest

from contextcliff.import_bridge.artifact_v1 import parse_artifact_v1
from contextcliff.runner.state import StateManager


class ImportBridgeTests(unittest.TestCase):
    def test_parse_fixture(self):
        here = os.path.dirname(__file__)
        path = os.path.join(here, "fixtures", "import_v1_min.json")
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        meta, rows = parse_artifact_v1(raw)
        self.assertIn("model", meta)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["example_id"], "e1")

    def test_parse_null_numerics(self):
        raw = {
            "schema_version": "1",
            "run_metadata": {},
            "predictions": [
                {
                    "example_id": "x",
                    "raw_output": "y",
                    "prompt_tokens": None,
                    "completion_tokens": None,
                    "latency_ms": None,
                    "f1_score": None,
                    "em_score": None,
                    "error": None,
                }
            ],
        }
        _, rows = parse_artifact_v1(raw)
        r = rows[0]
        self.assertEqual(r["prompt_tokens"], 0)
        self.assertEqual(r["completion_tokens"], 0)
        self.assertEqual(r["latency_ms"], 0.0)
        self.assertEqual(r["f1_score"], 0.0)
        self.assertEqual(r["em_score"], 0.0)

    def test_import_and_replace(self):
        fd, db = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            os.unlink(db)
        except OSError:
            pass
        sm = StateManager(db)
        meta = {"k": "v"}
        rows = [
            {
                "example_id": "a",
                "raw_output": "x",
                "prompt_tokens": 1,
                "completion_tokens": 2,
                "latency_ms": 0.0,
                "error": None,
                "f1_score": 0.1,
                "em_score": 0.0,
            }
        ]
        sm.import_external_run("rid1", "lab", None, meta, rows, replace=False)
        sm.import_external_run(
            "rid1",
            "lab2",
            "ref",
            {"k": "v2"},
            rows,
            replace=True,
        )
        p = sm.get_run_provenance("rid1")
        self.assertEqual(p["run_source"], "imported")
        self.assertEqual(p["external_label"], "lab2")
        self.assertEqual(p["artifact_ref"], "ref")

    def test_internal_blocked(self):
        fd, db = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            os.unlink(db)
        except OSError:
            pass
        sm = StateManager(db)
        sm.register_internal_run("internal-only", config={})
        meta = {"k": "v"}
        rows = [
            {
                "example_id": "a",
                "raw_output": "x",
                "prompt_tokens": 1,
                "completion_tokens": 2,
                "latency_ms": 0.0,
                "error": None,
                "f1_score": 0.0,
                "em_score": 0.0,
            }
        ]
        with self.assertRaises(ValueError) as cm:
            sm.import_external_run("internal-only", "lab", None, meta, rows, replace=False)
        self.assertIn("internal", str(cm.exception).lower())


if __name__ == "__main__":
    unittest.main()
