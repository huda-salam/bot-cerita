from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from .persistence import DB_PATH, init_db

def init_benchmark_db() -> None:
    init_db()
    with sqlite3.connect(DB_PATH) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS benchmark_cases (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, panel_prompts_json TEXT NOT NULL,
            reference_asset_ids_json TEXT NOT NULL, requirements_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS benchmark_runs (
            id TEXT PRIMARY KEY, case_id TEXT NOT NULL, provider TEXT NOT NULL,
            model TEXT NOT NULL, results_json TEXT NOT NULL, scores_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(case_id) REFERENCES benchmark_cases(id)
        );
        CREATE INDEX IF NOT EXISTS idx_benchmark_runs_case ON benchmark_runs(case_id);
        """)

def save_case(case) -> None:
    init_benchmark_db()
    with sqlite3.connect(DB_PATH) as db:
        db.execute("INSERT OR REPLACE INTO benchmark_cases VALUES(?,?,?,?,?,?)", (case.id, case.name, json.dumps(case.panel_prompts), json.dumps(case.reference_asset_ids), json.dumps(case.requirements), datetime.now(timezone.utc).isoformat()))
        db.commit()

def save_run(run) -> None:
    init_benchmark_db()
    with sqlite3.connect(DB_PATH) as db:
        db.execute("INSERT OR REPLACE INTO benchmark_runs VALUES(?,?,?,?,?,?,?)", (run.id, run.case_id, run.provider, run.model, json.dumps(run.results), json.dumps(run.scores), run.created_at))
        db.commit()
