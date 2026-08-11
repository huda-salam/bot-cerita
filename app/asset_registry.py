from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from uuid import uuid4
from .config import settings

@dataclass(frozen=True)
class CharacterAsset:
    id: str
    character_id: str
    asset_type: str
    file_path: str
    view: str = ""
    pose: str = ""
    expression: str = ""
    outfit: str = ""
    age: str = ""
    is_canon: bool = True
    source: str = "user_provided"


def _db_path() -> Path:
    url = settings.database_url
    return Path(url.removeprefix("sqlite:///")) if url.startswith("sqlite:///") else Path("bot_cerita.db")


def init_asset_table() -> None:
    with sqlite3.connect(_db_path()) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS character_assets (
            id TEXT PRIMARY KEY, character_id TEXT NOT NULL, asset_type TEXT NOT NULL,
            file_path TEXT NOT NULL, view TEXT NOT NULL DEFAULT '', pose TEXT NOT NULL DEFAULT '',
            expression TEXT NOT NULL DEFAULT '', outfit TEXT NOT NULL DEFAULT '', age TEXT NOT NULL DEFAULT '',
            is_canon INTEGER NOT NULL DEFAULT 1, source TEXT NOT NULL DEFAULT 'user_provided',
            created_at TEXT NOT NULL
        )""")
        db.execute("CREATE INDEX IF NOT EXISTS idx_character_assets_character ON character_assets(character_id)")
        db.commit()


def register_character_asset(character_id: str, file_path: str, asset_type: str = "visual_reference",
                             view: str = "", pose: str = "", expression: str = "", outfit: str = "",
                             age: str = "", is_canon: bool = True, source: str = "user_provided") -> CharacterAsset:
    init_asset_table()
    asset = CharacterAsset(str(uuid4()), character_id, asset_type, file_path, view, pose, expression, outfit, age, is_canon, source)
    with sqlite3.connect(_db_path()) as db:
        db.execute("INSERT INTO character_assets VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                   (asset.id, asset.character_id, asset.asset_type, asset.file_path, asset.view, asset.pose,
                    asset.expression, asset.outfit, asset.age, int(asset.is_canon), asset.source,
                    datetime.now(timezone.utc).isoformat()))
        db.commit()
    return asset


def list_character_assets(character_id: str) -> list[CharacterAsset]:
    init_asset_table()
    with sqlite3.connect(_db_path()) as db:
        rows = db.execute("SELECT id,character_id,asset_type,file_path,view,pose,expression,outfit,age,is_canon,source FROM character_assets WHERE character_id=? ORDER BY created_at", (character_id,)).fetchall()
    return [CharacterAsset(*r[:9], bool(r[9]), r[10]) for r in rows]
