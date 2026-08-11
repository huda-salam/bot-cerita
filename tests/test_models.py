from app.models import StoryRequest, Critique

def test_story_request_defaults():
    req = StoryRequest(idea="Anak menemukan naga kecil")
    assert req.target_age == "7-10"
    assert req.genre == "fantasy"

def test_critique_score_bounds():
    critique = Critique(
        overall_score=85,
        continuity=90,
        pacing=80,
        character=85,
        age_appropriateness=95,
        needs_revision=False,
    )
    assert critique.overall_score == 85
