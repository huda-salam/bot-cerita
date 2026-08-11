from dataclasses import dataclass
from pathlib import Path
import re

ROOT = Path(__file__).parent / "skills"

@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    content: str


def _frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    meta: dict[str, str] = {}
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
            if m:
                meta[m.group(1)] = m.group(2).strip().strip('"')
    return meta


def list_skills() -> list[Skill]:
    skills: list[Skill] = []
    for path in sorted(ROOT.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        meta = _frontmatter(content)
        skills.append(Skill(meta.get("name", path.stem), meta.get("description", ""), content))
    return skills


def select_skills(genre: str, target_age: str, tone: list[str]) -> list[Skill]:
    text = f"{genre} {target_age} {' '.join(tone)}".lower()
    selected: list[Skill] = []
    for skill in list_skills():
        keywords = [k.strip().lower() for k in re.split(r"[,;]", skill.description) if k.strip()]
        if skill.name in {"children_literature", "plot"}:
            selected.append(skill)
            continue
        if any(k in text for k in keywords) or any(k in text for k in skill.name.split("_")):
            selected.append(skill)
    return selected


def build_dynamic_skill_context(genre: str, target_age: str, tone: list[str]) -> str:
    return "\n\n--- DYNAMIC SKILL ---\n\n".join(s.content.strip() for s in select_skills(genre, target_age, tone))
