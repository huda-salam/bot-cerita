import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from .config import settings


def _db_path() -> str:
    url = settings.database_url
    if url.startswith("sqlite:///"):
        return url.removeprefix("sqlite:///")
    return "bot_cerita.db"


DB_PATH = Path(_db_path())


def init_db() -> None:
    if DB_PATH.parent != Path("."):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS stories (
                id TEXT PRIMARY KEY,
                title TEXT,
                status TEXT NOT NULL,
                request_json TEXT NOT NULL,
                state_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS agent_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id TEXT NOT NULL,
                agent TEXT NOT NULL,
                model TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                error TEXT
            );
            """
        )


def save_state(story_id: str, state: dict, status: str, title: str = "") -> None:
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            """INSERT INTO stories(id,title,status,request_json,state_json,created_at,updated_at)
               VALUES(?,?,?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET title=excluded.title,status=excluded.status,
               state_json=excluded.state_json,updated_at=excluded.updated_at""",
            (story_id, title, status, json.dumps(state.get("request", {}), ensure_ascii=False),
             json.dumps(state, ensure_ascii=False), now, now),
        )
        db.commit()


def record_agent_run(story_id: str, agent: str, model: str, status: str, started_at: str,
                     finished_at: str | None = None, error: str | None = None) -> None:
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            "INSERT INTO agent_runs(story_id,agent,model,status,started_at,finished_at,error) VALUES(?,?,?,?,?,?,?)",
            (story_id, agent, model, status, started_at, finished_at, error),
        )
        db.commit()
