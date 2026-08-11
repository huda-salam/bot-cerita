from typing import Literal
from pydantic import BaseModel, Field


class Character(BaseModel):
    name: str
    role: str
    traits: list[str] = Field(default_factory=list)
    description: str = ""
    appearance: str = ""


class Universe(BaseModel):
    id: str
    name: str
    description: str = ""
    canon_version: int = 1


class UniverseCreate(BaseModel):
    name: str
    description: str = ""


class CharacterCreate(BaseModel):
    name: str
    role: str = "supporting"
    traits: list[str] = Field(default_factory=list)
    description: str = ""
    appearance: str = ""


class CanonEntry(BaseModel):
    id: str
    category: str
    content: str
    authority: Literal["official", "established", "provisional", "non_canon"] = "established"


class CanonEntryCreate(BaseModel):
    category: str
    content: str
    authority: Literal["official", "established", "provisional", "non_canon"] = "established"


class StoryRequest(BaseModel):
    idea: str
    universe_id: str | None = None
    character_ids: list[str] = Field(default_factory=list)
    target_age: str = "7-10"
    genre: str = "fantasy"
    tone: list[str] = Field(default_factory=lambda: ["warm", "funny", "adventurous"])
    language: str = "Indonesian"
    length: Literal["short", "medium", "long"] = "medium"
    what_if_count: int = Field(default=5, ge=0, le=10)


class WhatIfCandidate(BaseModel):
    title: str
    premise: str
    hook: str
    conflict: str
    novelty_score: int = Field(ge=0, le=100)
    emotional_score: int = Field(ge=0, le=100)
    age_fit_score: int = Field(ge=0, le=100)
    overall_score: int = Field(ge=0, le=100)


class WhatIfResult(BaseModel):
    candidates: list[WhatIfCandidate]
    recommended_index: int = Field(ge=0)


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
    expert_guidance: str = ""
    universe_context: str = ""


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


class ExpertReview(BaseModel):
    expert: str
    score: int = Field(ge=0, le=100)
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ExpertPanel(BaseModel):
    reviews: list[ExpertReview] = Field(default_factory=list)


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
