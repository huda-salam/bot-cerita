from .models import StoryRequest
from .persistence import get_universe, list_characters, list_canon_entries


def resolve_universe_context(request: StoryRequest) -> str:
    if not request.universe_id:
        return ""
    universe = get_universe(request.universe_id)
    if not universe:
        raise ValueError(f"Universe not found: {request.universe_id}")

    characters = dict(list_characters(universe.id))
    selected = []
    for character_id in request.character_ids:
        character = characters.get(character_id)
        if character:
            selected.append({"id": character_id, **character.model_dump(mode="json")})

    canon = [entry.model_dump(mode="json") for entry in list_canon_entries(universe.id)]
    return (
        f"UNIVERSE: {universe.model_dump_json()}\n"
        f"SELECTED CHARACTERS: {selected}\n"
        f"CANON ENTRIES: {canon}\n"
        "CANON RULE: Official and established entries are binding. Provisional entries are hints, not facts. "
        "Non-canon entries must never be treated as canon. Do not invent contradictions. "
        "If the request conflicts with canon, preserve canon unless the user explicitly requests an alternate universe."
    )
