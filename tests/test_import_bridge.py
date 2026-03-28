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

    def test_missing_schema_version(self):
        with self.assertRaises(ValueError) as cm:
            parse_artifact_v1({"run_metadata": {}, "predictions": []})
        self.assertIn("schema_version", str(cm.exception))

    def test_unknown_schema_version(self):
        with self.assertRaises(ValueError) as cm:
            parse_artifact_v1(
                {
                    "schema_version": "2",
                    "run_metadata": {},
                    "predictions": [{"example_id": "a", "raw_output": "x"}],
                }
            )
        self.assertIn("Unsupported schema_version", str(cm.exception))

    def test_root_not_object(self):
        with self.assertRaises(ValueError) as cm:
            parse_artifact_v1([])
        self.assertIn("object", str(cm.exception).lower())

    def test_imported_duplicate_without_replace(self):
        fd, db = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            os.unlink(db)
        except OSError:
            pass
        sm = StateManager(db)
        row = {
            "example_id": "a",
            "raw_output": "x",
            "prompt_tokens": 1,
            "completion_tokens": 2,
            "latency_ms": 0.0,
            "error": None,
            "f1_score": 0.0,
            "em_score": 0.0,
        }
        sm.import_external_run("rid-dup", "lab", None, {}, [row], replace=False)
        with self.assertRaises(ValueError) as cm:
            sm.import_external_run("rid-dup", "lab2", "r2", {}, [row], replace=False)
        self.assertIn("replace", str(cm.exception).lower())

    def test_replace_removes_old_predictions(self):
        fd, db = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            os.unlink(db)
        except OSError:
            pass
        sm = StateManager(db)
        r1 = {
            "example_id": "a",
            "raw_output": "x",
            "prompt_tokens": 1,
            "completion_tokens": 2,
            "latency_ms": 0.0,
            "error": None,
            "f1_score": 0.0,
            "em_score": 0.0,
        }
        r2 = {
            "example_id": "b",
            "raw_output": "y",
            "prompt_tokens": 1,
            "completion_tokens": 2,
            "latency_ms": 0.0,
            "error": None,
            "f1_score": 0.0,
            "em_score": 0.0,
        }
        sm.import_external_run("rid-rep", "lab", None, {}, [r1, r2], replace=False)
        self.assertEqual(len(sm.get_run_data("rid-rep")), 2)
        sm.import_external_run(
            "rid-rep",
            "lab2",
            "ref",
            {"k": "v"},
            [r1],
            replace=True,
        )
        data = sm.get_run_data("rid-rep")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["example_id"], "a")

    def test_idempotent_replace_twice(self):
        fd, db = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            os.unlink(db)
        except OSError:
            pass
        sm = StateManager(db)
        row = {
            "example_id": "a",
            "raw_output": "x",
            "prompt_tokens": 1,
            "completion_tokens": 2,
            "latency_ms": 0.0,
            "error": None,
            "f1_score": 0.1,
            "em_score": 0.2,
        }
        meta = {"m": 1}
        for _ in range(2):
            sm.import_external_run("rid-idem", "L", "art", meta, [row], replace=True)
        d = sm.get_run_data("rid-idem")
        self.assertEqual(len(d), 1)
        self.assertAlmostEqual(d[0]["f1_score"], 0.1)
        p = sm.get_run_provenance("rid-idem")
        assert p is not None
        self.assertEqual(p["external_label"], "L")
        self.assertEqual(p["artifact_ref"], "art")


if __name__ == "__main__":
    unittest.main()
