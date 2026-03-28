
import sqlite3
import json
from typing import Optional, Dict, Any, List
from contextcliff.data.formats import Prediction, EvalRecord

_RUNS_PROVENANCE_ALTERS = (
    "ALTER TABLE runs ADD COLUMN run_source TEXT NOT NULL DEFAULT 'internal'",
    "ALTER TABLE runs ADD COLUMN external_label TEXT",
    "ALTER TABLE runs ADD COLUMN artifact_ref TEXT",
)


class StateManager:
    """Handles persistence of evaluation state (runs, results) to SQLite."""

    def __init__(self, db_path: str = "state.db"):
        self.db_path = db_path
        self._init_db()

    def _migrate_runs_provenance(self, cursor: sqlite3.Cursor) -> None:
        """Idempotent: provenance columns on ``runs``, defaults, backfill from ``predictions``."""
        for stmt in _RUNS_PROVENANCE_ALTERS:
            try:
                cursor.execute(stmt)
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise
        cursor.execute(
            """
            UPDATE runs SET run_source = 'internal'
            WHERE run_source IS NULL OR trim(run_source) = ''
            """
        )
        cursor.execute(
            """
            INSERT OR IGNORE INTO runs (run_id, timestamp, config, run_source, external_label, artifact_ref)
            SELECT DISTINCT p.run_id, CURRENT_TIMESTAMP, NULL, 'internal', NULL, NULL
            FROM predictions p
            WHERE NOT EXISTS (SELECT 1 FROM runs r WHERE r.run_id = p.run_id)
            """
        )

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

        self._migrate_runs_provenance(cursor)

        conn.commit()
        conn.close()

    def register_internal_run(
        self, run_id: str, config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register this process as an **internal** harness run (API/mock).

        Inserts or updates ``runs`` with ``run_source='internal'``. Merging runs from
        external experiments (``imported``) is Phase 3 — not handled here.

        On conflict for the same ``run_id``, ``run_source`` stays ``internal``,
        ``config`` and ``timestamp`` are updated, and nullable provenance fields are cleared.
        """
        if not run_id or not str(run_id).strip():
            raise ValueError("run_id must be non-empty")
        config_json = json.dumps(config) if config is not None else None
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO runs (run_id, timestamp, config, run_source, external_label, artifact_ref)
            VALUES (?, CURRENT_TIMESTAMP, ?, 'internal', NULL, NULL)
            ON CONFLICT(run_id) DO UPDATE SET
                config = excluded.config,
                timestamp = CURRENT_TIMESTAMP,
                run_source = 'internal',
                external_label = NULL,
                artifact_ref = NULL
            """,
            (run_id, config_json),
        )
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