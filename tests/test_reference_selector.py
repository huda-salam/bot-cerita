from app.reference_selector import select_references


def test_selector_prefers_exact_canon_match():
    assets = [
        {
            "id": "a1", "character_id": "c1", "is_canon": True,
            "view": "front", "pose": "standing", "expression": "happy",
            "outfit": "casual", "age": "child",
        },
        {
            "id": "a2", "character_id": "c1", "is_canon": True,
            "view": "side", "pose": "running", "expression": "angry",
            "outfit": "battle", "age": "child",
        },
    ]
    result = select_references(
        "c1", assets,
        {"view": "side", "pose": "running", "expression": "angry", "outfit": "battle", "age": "child"},
        limit=1,
    )
    assert result.selected[0]["id"] == "a2"
    assert result.candidates[0].score > result.candidates[1].score
    assert "canon" in result.candidates[0].reasons


def test_selector_excludes_other_characters():
    assets = [
        {"id": "wrong", "character_id": "c2", "is_canon": True},
        {"id": "right", "character_id": "c1", "is_canon": True},
    ]
    result = select_references("c1", assets, {}, limit=3)
    assert [a["id"] for a in result.selected] == ["right"]


def test_selector_returns_at_least_one_when_no_assets_match():
    result = select_references("c1", [], {"pose": "running"}, limit=3)
    assert result.selected == []
    assert result.candidates == []
