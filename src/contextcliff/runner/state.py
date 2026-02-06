
import sqlite3
import json
from typing import Optional, Dict, Any, List
from contextcliff.data.formats import Prediction, EvalRecord

class StateManager:
    """Handles persistence of evaluation state (runs, results) to SQLite."""

    def __init__(self, db_path: str = "state.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Runs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                config TEXT
            )
        ''')

        # Predictions table
        # We store raw output and metrics. 
        # For simplicity, we assume one prediction per example per run_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                run_id TEXT,
                example_id TEXT,
                raw_output TEXT,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                latency_ms REAL,
                error TEXT,
                PRIMARY KEY (run_id, example_id)
            )
        ''')

        # Metrics cache (separate or same? Let's keep same for now or compute on fly)
        # Actually, let's store metrics in predictions or a separate table.
        # Design doc mentions "Analysis reads from state.db".
        # Let's add metrics columns to predictions for simplicity
        try:
            cursor.execute("ALTER TABLE predictions ADD COLUMN f1_score REAL")
            cursor.execute("ALTER TABLE predictions ADD COLUMN em_score REAL")
        except sqlite3.OperationalError:
            pass # Columns exist

        conn.commit()
        conn.close()

    def save_prediction(self, run_id: str, example_id: str, pred: Prediction, metrics: EvalRecord):
        """Upsert a prediction record."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        error_msg = pred.parsed_output if pred.parsed_output and "Error" in pred.parsed_output else None

        cursor.execute('''
            INSERT INTO predictions (
                run_id, example_id, raw_output, prompt_tokens, completion_tokens, 
                latency_ms, error, f1_score, em_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id, example_id) DO UPDATE SET
                raw_output=excluded.raw_output,
                prompt_tokens=excluded.prompt_tokens,
                completion_tokens=excluded.completion_tokens,
                latency_ms=excluded.latency_ms,
                error=excluded.error,
                f1_score=excluded.f1_score,
                em_score=excluded.em_score
        ''', (
            run_id, 
            example_id, 
            pred.raw_output, 
            pred.usage.get("prompt_tokens", 0),
            pred.usage.get("completion_tokens", 0),
            pred.latency_ms,
            error_msg,
            metrics.f1_score,
            metrics.em_score
        ))
        
        conn.commit()
        conn.close()

    def get_completed_ids(self, run_id: str) -> List[str]:
        """Return list of example IDs that have been processed for this run."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT example_id FROM predictions WHERE run_id = ?", (run_id,))
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]

    def get_run_data(self, run_id: str) -> List[Dict[str, Any]]:
        """Fetch all data for a specific run (for analysis)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM predictions WHERE run_id = ?", (run_id,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows