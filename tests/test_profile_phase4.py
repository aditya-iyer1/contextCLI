"""Integration tests: CliffProfiler report sections (Phase 4)."""

import unittest

import pandas as pd

from contextcliff.analysis.cliff import CliffProfiler, ReportExtras


class ProfilePhase4ReportTests(unittest.TestCase):
    def _minimal_bins_df(self):
        return pd.DataFrame(
            {
                "min_tokens": [0, 1000],
                "max_tokens": [1000, 2000],
                "sample_count": [5, 5],
                "mean_f1": [0.9, 0.85],
                "std_f1": [0.05, 0.06],
                "failure_rate": [0.0, 0.1],
            }
        )

    def test_report_has_caveats_and_metrics_interpretation(self):
        cp = CliffProfiler()
        bins_df = self._minimal_bins_df()
        cliff_data = cp.detect_cliff(bins_df)
        extras = ReportExtras(
            filter_warnings=[],
            caveats_markdown="- Imported caveat.\n",
            metrics_interpretation_markdown="- **latency** note.\n",
            positional_markdown=None,
        )
        md = cp.generate_markdown_report(
            "rid",
            bins_df,
            cliff_data,
            provenance={"run_source": "imported", "external_label": "lab"},
            extras=extras,
        )
        self.assertIn("## Caveats", md)
        self.assertIn("### Metrics interpretation", md)
        self.assertIn("latency", md.lower())

    def test_compression_warning_surfaces_in_analysis_warnings(self):
        cp = CliffProfiler()
        bins_df = self._minimal_bins_df()
        cliff_data = cp.detect_cliff(bins_df)
        extras = ReportExtras(
            filter_warnings=[
                "compression_active_only was requested in analysis_filters but no manifest was provided"
            ],
            caveats_markdown=None,
            metrics_interpretation_markdown="- Latency note.\n",
            positional_markdown=None,
        )
        md = cp.generate_markdown_report(
            "rid", bins_df, cliff_data, provenance=None, extras=extras
        )
        self.assertIn("## Analysis warnings", md)
        self.assertIn("compression_active_only", md)

    def test_generate_markdown_without_extras_backward_compatible(self):
        cp = CliffProfiler()
        bins_df = self._minimal_bins_df()
        cliff_data = cp.detect_cliff(bins_df)
        md = cp.generate_markdown_report(
            "internal_run",
            bins_df,
            cliff_data,
            provenance={
                "run_source": "internal",
                "external_label": None,
                "config": "{}",
            },
            extras=None,
        )
        self.assertIn("ContextCliff Report", md)
        self.assertIn("## Executive Summary", md)
        self.assertNotIn("### Metrics interpretation", md)
        self.assertIn("run_source=`internal`", md)

    def test_positional_in_report(self):
        cp = CliffProfiler()
        bins_df = self._minimal_bins_df()
        cliff_data = cp.detect_cliff(bins_df)
        pos = (
            "## Positional diagnostics\n\n"
            "| Position bucket | Count | Mean F1 |\n|---|---|---|\n| early | 1 | 0.500 |\n\n"
        )
        extras = ReportExtras(
            filter_warnings=[],
            caveats_markdown=None,
            metrics_interpretation_markdown="- L.\n",
            positional_markdown=pos,
        )
        md = cp.generate_markdown_report("r", bins_df, cliff_data, provenance=None, extras=extras)
        self.assertIn("Positional diagnostics", md)


if __name__ == "__main__":
    unittest.main()
