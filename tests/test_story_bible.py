from app.models import Character, StorySpec
from app.orchestrator import build_initial_bible


def test_initial_story_bible_uses_story_spec():
    spec = StorySpec(
        title="Naga Kecil",
        premise="Anak menemukan naga",
        genre="fantasy",
        target_age="7-10",
        tone=["warm"],
        theme="friendship",
        setting="desa",
        characters=[Character(name="Raka", role="protagonist")],
        conflict="Naga ingin pulang",
        ending_direction="persahabatan",
    )
    bible = build_initial_bible(spec)
    assert bible.characters[0].name == "Raka"
    assert bible.locations == ["desa"]
    assert bible.unresolved_threads == ["Naga ingin pulang"]
