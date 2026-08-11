from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from uuid import uuid4
from .config import settings


@dataclass(frozen=True)
class WorldEntity:
    id: str
    universe_id: str
    entity_type: str
    name: str
    description: str = ""
    canon_status: str = "established"


def _db_path() -> Path:
    url = settings.database_url
    return Path(url.removeprefix("sqlite:///")) if url.startswith("sqlite:///") else Path("bot_cerita.db")


def init_world_tables() -> None:
    with sqlite3.connect(_db_path()) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS world_entities (
            id TEXT PRIMARY KEY, universe_id TEXT NOT NULL, entity_type TEXT NOT NULL,
            name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
            canon_status TEXT NOT NULL DEFAULT 'established', created_at TEXT NOT NULL
        )""")
        db.execute("CREATE INDEX IF NOT EXISTS idx_world_entities_universe ON world_entities(universe_id)")
        db.execute("""CREATE TABLE IF NOT EXISTS entity_relationships (
            id TEXT PRIMARY KEY, universe_id TEXT NOT NULL, source_id TEXT NOT NULL,
            target_id TEXT NOT NULL, relation TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
            valid_from TEXT, valid_until TEXT, created_at TEXT NOT NULL
        )""")
        db.execute("CREATE INDEX IF NOT EXISTS idx_relationships_source ON entity_relationships(source_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_relationships_target ON entity_relationships(target_id)")
        db.execute("""CREATE TABLE IF NOT EXISTS timeline_events (
            id TEXT PRIMARY KEY, universe_id TEXT NOT NULL, title TEXT NOT NULL,
            event_date TEXT, description TEXT NOT NULL DEFAULT '', canon_status TEXT NOT NULL DEFAULT 'established',
            created_at TEXT NOT NULL
        )""")
        db.execute("CREATE INDEX IF NOT EXISTS idx_timeline_universe ON timeline_events(universe_id)")
        db.commit()


def create_entity(universe_id: str, entity_type: str, name: str, description: str = "", canon_status: str = "established") -> WorldEntity:
    init_world_tables()
    entity = WorldEntity(str(uuid4()), universe_id, entity_type, name, description, canon_status)
    with sqlite3.connect(_db_path()) as db:
        db.execute("INSERT INTO world_entities VALUES (?,?,?,?,?,?,?)", (entity.id, entity.universe_id, entity.entity_type, entity.name, entity.description, entity.canon_status, datetime.now(timezone.utc).isoformat()))
        db.commit()
    return entity


def list_entities(universe_id: str, entity_type: str | None = None) -> list[WorldEntity]:
    init_world_tables()
    with sqlite3.connect(_db_path()) as db:
        if entity_type:
            rows = db.execute("SELECT id,universe_id,entity_type,name,description,canon_status FROM world_entities WHERE universe_id=? AND entity_type=? ORDER BY name", (universe_id, entity_type)).fetchall()
        else:
            rows = db.execute("SELECT id,universe_id,entity_type,name,description,canon_status FROM world_entities WHERE universe_id=? ORDER BY entity_type,name", (universe_id,)).fetchall()
    return [WorldEntity(*row) for row in rows]


def create_relationship(universe_id: str, source_id: str, target_id: str, relation: str, description: str = "", valid_from: str | None = None, valid_until: str | None = None) -> dict:
    init_world_tables()
    item = {"id": str(uuid4()), "universe_id": universe_id, "source_id": source_id, "target_id": target_id, "relation": relation, "description": description, "valid_from": valid_from, "valid_until": valid_until}
    with sqlite3.connect(_db_path()) as db:
        db.execute("INSERT INTO entity_relationships VALUES (?,?,?,?,?,?,?,?,?)", (*item.values(), datetime.now(timezone.utc).isoformat()))
        db.commit()
    return item


def list_relationships(universe_id: str, entity_id: str | None = None) -> list[dict]:
    init_world_tables()
    with sqlite3.connect(_db_path()) as db:
        if entity_id:
            rows = db.execute("SELECT id,universe_id,source_id,target_id,relation,description,valid_from,valid_until FROM entity_relationships WHERE universe_id=? AND (source_id=? OR target_id=?)", (universe_id, entity_id, entity_id)).fetchall()
        else:
            rows = db.execute("SELECT id,universe_id,source_id,target_id,relation,description,valid_from,valid_until FROM entity_relationships WHERE universe_id=?", (universe_id,)).fetchall()
    keys = ["id","universe_id","source_id","target_id","relation","description","valid_from","valid_until"]
    return [dict(zip(keys, row)) for row in rows]


def create_timeline_event(universe_id: str, title: str, description: str = "", event_date: str | None = None, canon_status: str = "established") -> dict:
    init_world_tables()
    item = {"id": str(uuid4()), "universe_id": universe_id, "title": title, "event_date": event_date, "description": description, "canon_status": canon_status}
    with sqlite3.connect(_db_path()) as db:
        db.execute("INSERT INTO timeline_events VALUES (?,?,?,?,?,?,?)", (*item.values(), datetime.now(timezone.utc).isoformat()))
        db.commit()
    return item


def list_timeline_events(universe_id: str) -> list[dict]:
    init_world_tables()
    with sqlite3.connect(_db_path()) as db:
        rows = db.execute("SELECT id,universe_id,title,event_date,description,canon_status FROM timeline_events WHERE universe_id=? ORDER BY event_date,created_at", (universe_id,)).fetchall()
    keys = ["id","universe_id","title","event_date","description","canon_status"]
    return [dict(zip(keys, row)) for row in rows]
