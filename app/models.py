from typing import Literal
from pydantic import BaseModel, Field


class Character(BaseModel):
    name: str
    role: str
    traits: list[str] = Field(default_factory=list)
    description: str = ""
    appearance: str = ""


class StoryRequest(BaseModel):
    idea: str
    target_age: str = "7-10"
    genre: str = "fantasy"
    tone: list[str] = Field(default_factory=lambda: ["warm", "funny", "adventurous"])
    language: str = "Indonesian"
    length: Literal["short", "medium", "long"] = "medium"


class StorySpec(BaseModel):
    title: str
    premise: str
    genre: str
    target_age: str
    tone: list[str]
    theme: str
    setting: str
    characters: list[Character]
    conflict: str
    ending_direction: str


class Scene(BaseModel):
    number: int
    title: str
    objective: str
    summary: str


class StoryOutline(BaseModel):
    title: str
    scenes: list[Scene]


class Story(BaseModel):
    title: str
    scenes: list[str]


class StoryBible(BaseModel):
    characters: list[Character] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)
    timeline: list[str] = Field(default_factory=list)
    unresolved_threads: list[str] = Field(default_factory=list)


class Critique(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    continuity: int = Field(ge=0, le=100)
    pacing: int = Field(ge=0, le=100)
    character: int = Field(ge=0, le=100)
    age_appropriateness: int = Field(ge=0, le=100)
    issues: list[str] = Field(default_factory=list)
    needs_revision: bool


class StoryResponse(BaseModel):
    id: str
    title: str
    story: str
    score: int
    revisions: int
