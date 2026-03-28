
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class ReportExtras:
    """Optional sections for ``generate_markdown_report`` (Phase 4 — ANA-01–ANA-04)."""

    filter_warnings: List[str] = field(default_factory=list)
    caveats_markdown: Optional[str] = None
    metrics_interpretation_markdown: str = ""
    positional_markdown: Optional[str] = None


class CliffProfiler:
    """Identifies the 'Cliff' and Safe Operating Cap."""

    def detect_cliff(self, bins_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Apply heuristic:
        Safe Cap = Max Length where (Mean > 0.7 * Baseline) AND (Var < 2.0 * Baseline)
        """
        if bins_df.empty:
            return {"error": "No data"}

        # 1. Calculate Baseline
        # Use first 3 bins (or fewer if total < 3)
        baseline_n = min(3, len(bins_df))
        baseline_bins = bins_df.head(baseline_n)
        
        # Weighted average for baseline mean/var? Or just simple mean of bins?
        # Simple mean of means is usually fine if bins are balanced.
        baseline_mean = baseline_bins['mean_f1'].mean()
        
        # Baseline variance (std^2). Average the stds? 
        # User specified "Var < 2.0 * Baseline". Assuming Baseline Variance.
        # Let's compute average variance of the baseline bins.
        # std_f1 is scalar in df.
        baseline_var = (baseline_bins['std_f1'] ** 2).mean()
        
        results = {
            "baseline_mean": baseline_mean,
            "baseline_var": baseline_var,
            "safe_cap_tokens": 0,
            "cliff_bin_index": -1,
            "status": "Stable"
        }
        
        # 2. Iterate and Check
        # We look for the FIRST bin that violates the condition.
        # The Safe Cap is the upper bound of the PREVIOUS bin (the last good one).
        
        for i, row in bins_df.iterrows():
            curr_mean = row['mean_f1']
            curr_var = row['std_f1'] ** 2
            
            is_mean_good = curr_mean > (0.7 * baseline_mean)
            
            # If baseline_var is very small (e.g. 0), we need a fallback or smoothing
            # to avoid infinite sensitivity. 
            # If baseline_var < 1e-4, treat as 1e-4?
            effective_base_var = max(baseline_var, 1e-4)
            is_var_good = curr_var < (2.0 * effective_base_var)
            
            if not is_mean_good or not is_var_good:
                # Found the cliff (or transition)!
                results['cliff_bin_index'] = i
                results['cliff_reason'] = []
                if not is_mean_good: results['cliff_reason'].append("Mean Drop")
                if not is_var_good: results['cliff_reason'].append("Variance Spike")
                
                # Safe cap is max_tokens of the *previous* bin. 
                # If i=0 (fails immediately), safe cap is 0 or min_tokens?
                if i > 0:
                    prev_row = bins_df.iloc[i-1]
                    results['safe_cap_tokens'] = prev_row['max_tokens']
                else:
                    results['safe_cap_tokens'] = row['min_tokens'] # Fails start
                
                results['status'] = "Cliff Detected"
                break
        
        # If loop finishes without break, model is stable throughout
        if results['status'] == "Stable":
            results['safe_cap_tokens'] = bins_df.iloc[-1]['max_tokens']
            
        return results

    def generate_markdown_report(
        self,
        run_id: str,
        bins_df: pd.DataFrame,
        cliff_data: Dict[str, Any],
        provenance: Optional[Dict[str, Any]] = None,
        extras: Optional[ReportExtras] = None,
    ) -> str:
        """Generates the markdown table and summary.

        Section order: Provenance → Analysis warnings → Executive Summary (incl. metrics
        interpretation) → Performance by Length Bin → Positional diagnostics → Caveats.
        """
        
        md = f"# ContextCliff Report: Run {run_id}\n\n"
        if provenance:
            rs = provenance.get("run_source")
            el = provenance.get("external_label")
            ar = provenance.get("artifact_ref")
            parts = []
            if rs is not None:
                parts.append(f"run_source=`{str(rs)}`")
            if el is not None:
                el_s = str(el).replace("\n", " ").replace("`", "'")
                parts.append(f"external_label=`{el_s}`")
            if ar is not None and str(ar).strip():
                ar_s = str(ar).replace("\n", " ").replace("`", "'")
                parts.append(f"artifact_ref=`{ar_s}`")
            if parts:
                md += "**Provenance:** " + " · ".join(parts) + "\n\n"

        if extras and extras.filter_warnings:
            md += "## Analysis warnings\n\n"
            for w in extras.filter_warnings:
                md += f"- {w}\n"
            md += "\n"

        md += "## Executive Summary\n"
        if extras and extras.metrics_interpretation_markdown.strip():
            md += "### Metrics interpretation\n\n"
            md += extras.metrics_interpretation_markdown.strip() + "\n\n"
        md += f"- **Safe Operating Cap**: {int(cliff_data['safe_cap_tokens'])} tokens\n"
        md += f"- **Baseline Performance**: F1={cliff_data['baseline_mean']:.3f} (approx)\n"
        if 'cliff_reason' in cliff_data:
            md += f"- **Cliff Triggers**: {', '.join(cliff_data['cliff_reason'])}\n"
        else:
            md += "- **Status**: Stable across all tested lengths.\n"
            
        # Table
        md += "\n## Performance by Length Bin\n"
        md += "| Bin Range (Tokens) | Samples | Mean F1 | Std F1 | Failure Rate |\n"
        md += "|---|---|---|---|---|\n"
        
        for _, row in bins_df.iterrows():
            range_str = f"{int(row['min_tokens'])}-{int(row['max_tokens'])}"
            md += f"| {range_str} | {int(row['sample_count'])} | {row['mean_f1']:.3f} | {row['std_f1']:.3f} | {row['failure_rate']:.1%} |\n"

        if extras and extras.positional_markdown:
            md += "\n" + extras.positional_markdown.rstrip() + "\n"

        if extras and extras.caveats_markdown:
            md += "\n## Caveats\n\n"
            md += extras.caveats_markdown.strip() + "\n"
            
        return md
