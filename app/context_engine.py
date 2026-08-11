from dataclasses import dataclass
from .persistence import get_universe, list_characters, list_canon_entries
from .world_model import list_entities, list_relationships, list_timeline_events

@dataclass
class ContextPack:
    universe: str
    characters: list[dict]
    canon: list[dict]
    world_entities: list[dict]
    relationships: list[dict]
    timeline: list[dict]
    warnings: list[str]

    def as_text(self) -> str:
        parts = ["UNIVERSE:\n" + self.universe]
        for label, items in (("CHARACTERS", self.characters), ("CANON", self.canon), ("WORLD ENTITIES", self.world_entities), ("RELATIONSHIPS", self.relationships), ("TIMELINE", self.timeline)):
            if items:
                parts.append(label + ":\n" + "\n".join(str(x) for x in items))
        if self.warnings:
            parts.append("CONTEXT WARNINGS:\n" + "\n".join(self.warnings))
        return "\n\n".join(parts)


def _relevance(text: str, query: str) -> int:
    tokens = {x.lower() for x in query.split() if len(x) > 2}
    haystack = text.lower()
    return sum(1 for token in tokens if token in haystack)


def build_context_pack(universe_id: str, character_ids: list[str], query: str, max_items: int = 40) -> ContextPack:
    universe = get_universe(universe_id)
    if not universe:
        raise ValueError("Universe not found")
    characters = []
    for cid, character in list_characters(universe_id):
        if not character_ids or cid in character_ids:
            item = {"id": cid, **character.model_dump(mode="json")}
            item["_score"] = _relevance(str(item), query) + (10 if cid in character_ids else 0)
            characters.append(item)
    characters.sort(key=lambda x: x["_score"], reverse=True)
    canon = [x.model_dump(mode="json") for x in list_canon_entries(universe_id)]
    canon.sort(key=lambda x: _relevance(str(x), query), reverse=True)
    entities = [x.__dict__ for x in list_entities(universe_id)]
    entities.sort(key=lambda x: _relevance(str(x), query), reverse=True)
    relationships = list_relationships(universe_id)
    relationships.sort(key=lambda x: _relevance(str(x), query), reverse=True)
    timeline = list_timeline_events(universe_id)
    timeline.sort(key=lambda x: _relevance(str(x), query), reverse=True)
    warnings = []
    if any(x.get("canon_status") == "non_canon" for x in canon[:max_items]):
        warnings.append("Non-canon material exists; do not treat it as established canon unless the user explicitly requests an AU/non-canon story.")
    if any(x.get("canon_status") == "provisional" for x in canon[:max_items]):
        warnings.append("Some retrieved canon is provisional and should not be presented as certain fact.")
    return ContextPack(universe.model_dump_json(), characters[:max_items], canon[:max_items], entities[:max_items], relationships[:max_items], timeline[:max_items], warnings)
