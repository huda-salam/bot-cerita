from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ReferenceCandidate:
    asset: dict
    score: int
    reasons: list[str]

@dataclass(frozen=True)
class ReferenceSelection:
    character_id: str
    selected: list[dict]
    candidates: list[ReferenceCandidate]

def _score(asset: dict, requested: dict) -> tuple[int, list[str]]:
    score=0; reasons=[]
    for key,weight in (("view",4),("pose",4),("expression",3),("outfit",3),("age",2)):
        wanted=(requested.get(key) or "").strip().lower(); actual=(asset.get(key) or "").strip().lower()
        if not wanted: continue
        if actual == wanted: score+=weight; reasons.append(f"{key}: exact")
        elif actual and (wanted in actual or actual in wanted): score+=max(1,weight//2); reasons.append(f"{key}: compatible")
    if asset.get("is_canon",True): score+=5; reasons.append("canon")
    return score,reasons

def select_references(character_id: str, assets: list[dict], requested: dict, limit: int=3) -> ReferenceSelection:
    candidates=[]
    for asset in assets:
        if asset.get("character_id") not in (None,character_id): continue
        score,reasons=_score(asset,requested); candidates.append(ReferenceCandidate(asset,score,reasons))
    candidates.sort(key=lambda c:c.score,reverse=True)
    return ReferenceSelection(character_id,[c.asset for c in candidates[:max(1,limit)]],candidates)
