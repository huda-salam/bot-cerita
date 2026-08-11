import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from .config import settings
from .models import Universe, UniverseCreate, Character, CharacterCreate


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
        db.executescript("""
            CREATE TABLE IF NOT EXISTS stories (
                id TEXT PRIMARY KEY, title TEXT, status TEXT NOT NULL,
                request_json TEXT NOT NULL, state_json TEXT NOT NULL,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS agent_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT, story_id TEXT NOT NULL,
                agent TEXT NOT NULL, model TEXT NOT NULL, status TEXT NOT NULL,
                started_at TEXT NOT NULL, finished_at TEXT, error TEXT
            );
            CREATE TABLE IF NOT EXISTS universes (
                id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL DEFAULT '', canon_version INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS characters (
                id TEXT PRIMARY KEY, universe_id TEXT NOT NULL, name TEXT NOT NULL,
                role TEXT NOT NULL, traits_json TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '', appearance TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                FOREIGN KEY(universe_id) REFERENCES universes(id)
            );
            CREATE INDEX IF NOT EXISTS idx_characters_universe ON characters(universe_id);
        """)


def save_state(story_id: str, state: dict, status: str, title: str = "") -> None:
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""INSERT INTO stories(id,title,status,request_json,state_json,created_at,updated_at)
           VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET title=excluded.title,status=excluded.status,
           state_json=excluded.state_json,updated_at=excluded.updated_at""",
           (story_id, title, status, json.dumps(state.get("request", {}), ensure_ascii=False),
            json.dumps(state, ensure_ascii=False), now, now))
        db.commit()


def record_agent_run(story_id: str, agent: str, model: str, status: str, started_at: str,
                     finished_at: str | None = None, error: str | None = None) -> None:
    with sqlite3.connect(DB_PATH) as db:
        db.execute("INSERT INTO agent_runs(story_id,agent,model,status,started_at,finished_at,error) VALUES(?,?,?,?,?,?,?)",
                   (story_id, agent, model, status, started_at, finished_at, error))
        db.commit()


def create_universe(data: UniverseCreate) -> Universe:
    init_db()
    universe = Universe(id=str(uuid4()), name=data.name, description=data.description)
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as db:
        db.execute("INSERT INTO universes(id,name,description,canon_version,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                   (universe.id, universe.name, universe.description, universe.canon_version, now, now))
        db.commit()
    return universe


def list_universes() -> list[Universe]:
    init_db()
    with sqlite3.connect(DB_PATH) as db:
        rows = db.execute("SELECT id,name,description,canon_version FROM universes ORDER BY name").fetchall()
    return [Universe(id=r[0], name=r[1], description=r[2], canon_version=r[3]) for r in rows]


def get_universe(universe_id: str) -> Universe | None:
    init_db()
    with sqlite3.connect(DB_PATH) as db:
        r = db.execute("SELECT id,name,description,canon_version FROM universes WHERE id=?", (universe_id,)).fetchone()
    return Universe(id=r[0], name=r[1], description=r[2], canon_version=r[3]) if r else None


def create_character(universe_id: str, data: CharacterCreate) -> tuple[str, Character] | None:
    if not get_universe(universe_id):
        return None
    character = Character(name=data.name, role=data.role, traits=data.traits,
                          description=data.description, appearance=data.appearance)
    character_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as db:
        db.execute("INSERT INTO characters(id,universe_id,name,role,traits_json,description,appearance,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
                   (character_id, universe_id, character.name, character.role,
                    json.dumps(character.traits, ensure_ascii=False), character.description,
                    character.appearance, now, now))
        db.commit()
    return character_id, character


def list_characters(universe_id: str) -> list[tuple[str, Character]]:
    init_db()
    with sqlite3.connect(DB_PATH) as db:
        rows = db.execute("SELECT id,name,role,traits_json,description,appearance FROM characters WHERE universe_id=? ORDER BY name", (universe_id,)).fetchall()
    return [(r[0], Character(name=r[1], role=r[2], traits=json.loads(r[3]), description=r[4], appearance=r[5])) for r in rows]
