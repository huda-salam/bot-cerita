import pytest
from pydantic import ValidationError
from app.models import StoryRequest, WhatIfCandidate, Critique


def test_story_request_defaults():
    req = StoryRequest(idea="Anak menemukan naga kecil")
    assert req.target_age == "7-10"
    assert req.genre == "fantasy"
    assert req.language == "Indonesian"
    assert req.length == "medium"
    assert req.what_if_count == 5


def test_story_request_rejects_invalid_length():
    with pytest.raises(ValidationError):
        StoryRequest(idea="x", length="huge")


def test_story_request_rejects_out_of_range_what_if_count():
    with pytest.raises(ValidationError):
        StoryRequest(idea="x", what_if_count=11)


def test_what_if_candidate_score_bounds():
    candidate = WhatIfCandidate(
        title="Tes", premise="P", hook="H", conflict="C",
        novelty_score=80, emotional_score=70, age_fit_score=90, overall_score=85,
    )
    assert candidate.overall_score == 85
    with pytest.raises(ValidationError):
        WhatIfCandidate(
            title="Tes", premise="P", hook="H", conflict="C",
            novelty_score=101, emotional_score=70, age_fit_score=90, overall_score=85,
        )


def test_critique_schema():
    critique = Critique(
        overall_score=85, continuity=90, pacing=80, character=85,
        age_appropriateness=95, needs_revision=False,
    )
    assert critique.overall_score == 85
    assert critique.needs_revision is False
