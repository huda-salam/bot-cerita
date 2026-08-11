from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

@dataclass
class StoryProject:
    id: str
    universe_id: str | None
    title: str
    status: str = "draft"
    scenes: list[dict[str, Any]] = field(default_factory=list)
    selected_characters: list[str] = field(default_factory=list)
    style_bible: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

class StoryStudio:
    def __init__(self):
        self.projects: dict[str, StoryProject] = {}
    def create(self, title: str, universe_id: str | None = None) -> StoryProject:
        project = StoryProject(str(uuid4()), universe_id, title)
        self.projects[project.id] = project
        return project
    def get(self, project_id: str) -> StoryProject | None:
        return self.projects.get(project_id)
    def update(self, project_id: str, **changes) -> StoryProject:
        project = self.projects[project_id]
        for key, value in changes.items():
            if hasattr(project, key) and value is not None:
                setattr(project, key, value)
        return project

studio = StoryStudio()
