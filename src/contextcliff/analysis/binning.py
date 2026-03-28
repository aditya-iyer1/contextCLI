
import sqlite3
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple

class ResultBinner:
    """Aggregates raw predictions into length bins for analysis."""

    def __init__(self, db_path: str = "state.db"):
        self.db_path = db_path

    def load_run_data(self, run_id: str) -> pd.DataFrame:
        """Loads predictions and metrics for a run into a DataFrame."""
        conn = sqlite3.connect(self.db_path)
        # We need context_tokens. In current schema, predictions table has 'prompt_tokens'
        # which is roughly context tokens (plus query). 
        # Alternatively, join with manifest info if needed, but prompt_tokens is accurate for actual run.
        df = pd.read_sql_query(
            "SELECT * FROM predictions WHERE run_id = ?",
            conn,
            params=(run_id,),
        )
        conn.close()
        
        # Ensure numeric types
        cols = ['prompt_tokens', 'completion_tokens', 'f1_score', 'em_score', 'latency_ms']
        for c in cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce')
        
        return df

    def bin_results(self, df: pd.DataFrame, n_bins: int = 10) -> pd.DataFrame:
        """
        bins the dataframe by 'prompt_tokens' and computes aggregates.
        """
        if df.empty:
            return pd.DataFrame()

        # Create bins based on quantiles (using prompt_tokens)
        try:
            df['bin'] = pd.qcut(df['prompt_tokens'], q=n_bins, duplicates='drop')
        except ValueError:
            # Fallback if specific quantiles fail (e.g. not enough unique values)
             df['bin'] = pd.cut(df['prompt_tokens'], bins=n_bins)
        
        # Aggregate
        stats = df.groupby('bin', observed=True).agg(
            sample_count=('example_id', 'count'),
            min_tokens=('prompt_tokens', 'min'),
            max_tokens=('prompt_tokens', 'max'),
            mean_f1=('f1_score', 'mean'),
            std_f1=('f1_score', 'std'),
            mean_em=('em_score', 'mean'),
            failure_rate=('error', lambda x: x.notna().mean())
        ).reset_index()
        
        # Fill NaN std with 0 (single sample bins)
        stats['std_f1'] = stats['std_f1'].fillna(0.0)
        
        return stats
