"""Unit tests for analysis/profile_report helpers (Phase 4)."""

import unittest

import pandas as pd

from contextcliff.analysis.profile_report import (
    ANALYSIS_FILTERS_KEY,
    apply_prediction_filters,
    build_caveats_section,
    build_metrics_interpretation_note,
    build_positional_section,
    effective_filters,
    load_manifest_df,
    parse_run_config,
)


class ProfileReportHelpersTests(unittest.TestCase):
    def test_parse_run_config_invalid_json_warns(self):
        d, w = parse_run_config("{not json")
        self.assertEqual(d, {})
        self.assertTrue(any("valid JSON" in x for x in w))

    def test_effective_filters_cli_overrides(self):
        rc = {ANALYSIS_FILTERS_KEY: {"min_prompt_tokens": 100, "max_prompt_tokens": 9000}}
        f = effective_filters(rc, 200, None)
        self.assertEqual(f["min_prompt_tokens"], 200)
        self.assertEqual(f["max_prompt_tokens"], 9000)

    def test_token_filters(self):
        df = pd.DataFrame(
            {
                "example_id": ["a", "b", "c"],
                "prompt_tokens": [50, 500, 5000],
                "f1_score": [0.5, 0.6, 0.7],
            }
        )
        out, w = apply_prediction_filters(
            df, {"min_prompt_tokens": 100, "max_prompt_tokens": 2000}, None
        )
        self.assertEqual(len(out), 1)
        self.assertEqual(out.iloc[0]["example_id"], "b")
        self.assertEqual(w, [])

    def test_compression_filter_requires_manifest_warning(self):
        df = pd.DataFrame(
            {
                "example_id": ["a"],
                "prompt_tokens": [100],
                "f1_score": [0.5],
            }
        )
        out, w = apply_prediction_filters(df, {"compression_active_only": True}, None)
        self.assertEqual(len(out), 1)
        self.assertTrue(any("manifest" in x.lower() for x in w))

    def test_compression_filter_with_manifest(self):
        df = pd.DataFrame(
            {
                "example_id": ["a", "b"],
                "prompt_tokens": [100, 200],
                "f1_score": [0.5, 0.6],
            }
        )
        mdf = pd.DataFrame(
            {
                "id": ["a", "b"],
                "metadata": [
                    {"compression_active": True},
                    {"compression_active": False},
                ],
            }
        )
        out, w = apply_prediction_filters(
            df, {"compression_active_only": True}, mdf
        )
        self.assertEqual(len(out), 1)
        self.assertEqual(out.iloc[0]["example_id"], "a")
        self.assertEqual(w, [])

    def test_build_caveats_imported_includes_experimental_conditions(self):
        text = build_caveats_section(
            {"run_source": "imported", "external_label": "x"},
            {},
        )
        assert text is not None
        self.assertIn("F1", text)
        self.assertIn("experimental", text.lower())

    def test_positional_section(self):
        df = pd.DataFrame(
            {
                "example_id": ["a", "b"],
                "prompt_tokens": [100, 200],
                "f1_score": [0.5, 0.8],
            }
        )
        mdf = pd.DataFrame(
            {
                "id": ["a", "b"],
                "metadata": [
                    {"needle_position_bucket": "early"},
                    {"needle_position_bucket": "late"},
                ],
            }
        )
        md = build_positional_section(df, mdf)
        assert md is not None
        self.assertIn("Positional diagnostics", md)
        self.assertIn("early", md)

    def test_metrics_note_latency_not_throughput(self):
        note = build_metrics_interpretation_note({}, {})
        self.assertIn("latency_ms", note)
        self.assertIn("Throughput", note)
        self.assertIn("not", note.lower())


if __name__ == "__main__":
    unittest.main()
