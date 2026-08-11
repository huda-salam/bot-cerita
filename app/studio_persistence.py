from __future__ import annotations
import sqlite3, json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from .config import settings

def _db_path() -> Path:
    url = settings.database_url
    return Path(url.removeprefix("sqlite:///")) if url.startswith("sqlite:///") else Path("bot_cerita.db")

def init_studio_tables() -> None:
    with sqlite3.connect(_db_path()) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS story_projects (id TEXT PRIMARY KEY, universe_id TEXT, title TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'draft', style_bible TEXT NOT NULL DEFAULT '', metadata TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS story_project_characters (project_id TEXT NOT NULL, character_id TEXT NOT NULL, PRIMARY KEY(project_id, character_id));
        CREATE TABLE IF NOT EXISTS story_scenes (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, scene_number INTEGER NOT NULL, title TEXT NOT NULL DEFAULT '', summary TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'draft', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS story_panels (id TEXT PRIMARY KEY, scene_id TEXT NOT NULL, panel_number INTEGER NOT NULL, purpose TEXT NOT NULL DEFAULT '', shot TEXT NOT NULL DEFAULT '', camera TEXT NOT NULL DEFAULT '', action TEXT NOT NULL DEFAULT '', expression TEXT NOT NULL DEFAULT '', dialogue TEXT NOT NULL DEFAULT '', narration TEXT NOT NULL DEFAULT '', visual_prompt TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS panel_reference_assets (panel_id TEXT NOT NULL, asset_id TEXT NOT NULL, character_id TEXT NOT NULL, selection_reason TEXT NOT NULL DEFAULT '', PRIMARY KEY(panel_id, asset_id));
        CREATE TABLE IF NOT EXISTS image_generations (id TEXT PRIMARY KEY, panel_id TEXT NOT NULL, provider TEXT NOT NULL, model TEXT NOT NULL, url TEXT NOT NULL DEFAULT '', file_path TEXT NOT NULL DEFAULT '', seed INTEGER, parent_image_id TEXT, reference_assets TEXT NOT NULL DEFAULT '[]', metadata TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL);
        """)

def _now(): return datetime.now(timezone.utc).isoformat()

def create_project(title, universe_id=None):
    init_studio_tables(); now=_now(); item={"id":str(uuid4()),"universe_id":universe_id,"title":title,"status":"draft","style_bible":"","metadata":{},"created_at":now,"updated_at":now}
    with sqlite3.connect(_db_path()) as db: db.execute("INSERT INTO story_projects VALUES (?,?,?,?,?,?,?,?)", (item["id"],universe_id,title,"draft","",json.dumps({}),now,now)); db.commit()
    return item

def get_project(project_id):
    init_studio_tables()
    with sqlite3.connect(_db_path()) as db: row=db.execute("SELECT id,universe_id,title,status,style_bible,metadata,created_at,updated_at FROM story_projects WHERE id=?",(project_id,)).fetchone()
    if not row:return None
    keys=["id","universe_id","title","status","style_bible","metadata","created_at","updated_at"]; item=dict(zip(keys,row)); item["metadata"]=json.loads(item["metadata"] or "{}"); return item

def update_project(project_id, **changes):
    project=get_project(project_id)
    if not project: return None
    allowed={k:v for k,v in changes.items() if k in {"title","status","style_bible","metadata"} and v is not None}
    if not allowed: return project
    if isinstance(allowed.get("metadata"),dict): allowed["metadata"]=json.dumps(allowed["metadata"])
    allowed["updated_at"]=_now()
    with sqlite3.connect(_db_path()) as db:
        sets=", ".join(f"{k}=?" for k in allowed); db.execute(f"UPDATE story_projects SET {sets} WHERE id=?", (*allowed.values(),project_id)); db.commit()
    return get_project(project_id)

def add_scene(project_id, scene_number, title="", summary=""):
    init_studio_tables(); now=_now(); item={"id":str(uuid4()),"project_id":project_id,"scene_number":scene_number,"title":title,"summary":summary,"status":"draft","created_at":now,"updated_at":now}
    with sqlite3.connect(_db_path()) as db: db.execute("INSERT INTO story_scenes VALUES (?,?,?,?,?,?,?,?)",tuple(item.values())); db.commit()
    return item

def list_scenes(project_id):
    init_studio_tables()
    with sqlite3.connect(_db_path()) as db: rows=db.execute("SELECT id,project_id,scene_number,title,summary,status,created_at,updated_at FROM story_scenes WHERE project_id=? ORDER BY scene_number",(project_id,)).fetchall()
    keys=["id","project_id","scene_number","title","summary","status","created_at","updated_at"]; return [dict(zip(keys,r)) for r in rows]

def add_panel(scene_id,panel_number,**v):
    init_studio_tables(); now=_now(); item={"id":str(uuid4()),"scene_id":scene_id,"panel_number":panel_number,"purpose":v.get("purpose",""),"shot":v.get("shot",""),"camera":v.get("camera",""),"action":v.get("action",""),"expression":v.get("expression",""),"dialogue":v.get("dialogue",""),"narration":v.get("narration",""),"visual_prompt":v.get("visual_prompt",""),"created_at":now,"updated_at":now}
    with sqlite3.connect(_db_path()) as db: db.execute("INSERT INTO story_panels VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",tuple(item.values())); db.commit()
    return item

def get_panel(panel_id):
    init_studio_tables()
    with sqlite3.connect(_db_path()) as db: row=db.execute("SELECT id,scene_id,panel_number,purpose,shot,camera,action,expression,dialogue,narration,visual_prompt FROM story_panels WHERE id=?",(panel_id,)).fetchone()
    if not row:return None
    keys=["id","scene_id","panel_number","purpose","shot","camera","action","expression","dialogue","narration","visual_prompt"]; return dict(zip(keys,row))

def set_panel_references(panel_id, references):
    init_studio_tables()
    with sqlite3.connect(_db_path()) as db:
        db.execute("DELETE FROM panel_reference_assets WHERE panel_id=?",(panel_id,))
        db.executemany("INSERT INTO panel_reference_assets(panel_id,asset_id,character_id,selection_reason) VALUES (?,?,?,?)",[(panel_id,r["asset_id"],r["character_id"],r.get("reason", "manual selection")) for r in references]); db.commit()
    return list_panel_references(panel_id)

def list_panel_references(panel_id):
    init_studio_tables()
    with sqlite3.connect(_db_path()) as db: rows=db.execute("SELECT asset_id,character_id,selection_reason FROM panel_reference_assets WHERE panel_id=? ORDER BY character_id,asset_id",(panel_id,)).fetchall()
    return [{"asset_id":r[0],"character_id":r[1],"reason":r[2]} for r in rows]
