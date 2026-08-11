from __future__ import annotations
import sqlite3
from pathlib import Path
from .config import settings
from .asset_registry import list_character_assets

def _db_path() -> Path:
    url = settings.database_url
    return Path(url.removeprefix("sqlite:///")) if url.startswith("sqlite:///") else Path("bot_cerita.db")

def attach_character(project_id: str, character_id: str) -> None:
    with sqlite3.connect(_db_path()) as db:
        db.execute("INSERT OR IGNORE INTO story_project_characters(project_id, character_id) VALUES (?,?)", (project_id, character_id)); db.commit()

def list_project_characters(project_id: str) -> list[str]:
    with sqlite3.connect(_db_path()) as db:
        return [r[0] for r in db.execute("SELECT character_id FROM story_project_characters WHERE project_id=? ORDER BY character_id", (project_id,)).fetchall()]

def project_reference_assets(project_id: str) -> list[dict]:
    result=[]
    for character_id in list_project_characters(project_id):
        for asset in list_character_assets(character_id):
            if asset.is_canon:
                result.append({"character_id":character_id,"asset_id":asset.id,"file_path":asset.file_path,"view":asset.view,"pose":asset.pose,"expression":asset.expression,"outfit":asset.outfit,"age":asset.age})
    return result
